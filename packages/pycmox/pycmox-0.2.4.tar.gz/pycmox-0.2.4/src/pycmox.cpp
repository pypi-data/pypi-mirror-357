/*
 * Copyright (c) 2021-2023, Matwey V. Kornilov <matwey.kornilov@gmail.com>
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 *
 */

#include <string>
#include <memory>
#include <vector>

#include <pybind11/pybind11.h>

#include <exchange.h>


namespace py = pybind11;


class rs485 {
public:
	rs485(const std::string& filename, int baudrate):
		impl_{RS485ImplFactory(filename, baudrate).create()} {
	}
	rs485(const rs485&) = delete;
	rs485(rs485&&) = delete;
	rs485& operator=(const rs485&) = delete;
	rs485& operator=(rs485&&) = delete;
	~rs485() = default;

	int askByte(unsigned int addr, int c) {
		return impl_->askByte(addr, AByte(c));
	}
	int askWord(unsigned int addr, int c) {
		return impl_->askWord(addr, AWord(c));
	}
	int askLong(unsigned int addr, int c) {
		return impl_->askLong(addr, ALong(c));
	}
	py::bytes askData(unsigned int addr, int c) {
		const auto vec = impl_->askData(addr, AData(c));

		return py::bytes(reinterpret_cast<const char*>(vec.data()), vec.size());
	}
	py::bytes askRaw(const py::buffer& data) {
		const auto info = data.request();
		const auto begin = reinterpret_cast<const unsigned char*>(info.ptr);
		const auto end = begin + static_cast<std::size_t>(info.size);
		const auto vec = impl_->askRaw(std::vector<unsigned char>(begin, end));

		return py::bytes(reinterpret_cast<const char*>(vec.data()), vec.size());
	}

	int sendSimpleCommand(unsigned int addr, int c) {
		return impl_->sendSimpleCommand(addr, SComm(c));
	}
	int sendByteCommand(unsigned int addr, int c, int b) {
		return impl_->sendByteCommand(addr, SByte(c), b);
	}
	int sendWordCommand(unsigned int addr, int c, int w) {
		return impl_->sendWordCommand(addr, SWord(c), w);
	}
	int sendData(unsigned int addr, const py::buffer& data) {
		const auto info = data.request();
		const auto begin = reinterpret_cast<const unsigned char*>(info.ptr);
		const auto end = begin + static_cast<std::size_t>(info.size);
		const std::vector<unsigned char> vec(begin, end);

		return impl_->sendData(addr, vec.size(), vec);
	}

	constexpr static const char* docstring = R"(
RS485 device object

Methods
-------
askByte(address, command)
	Ask the device for a byte of data.
askWord(address, command)
	Ask the device for a word of data.
askLong(address, command)
	Ask the device for a double word of data.
askData(address, command)
	Ask the device for a variable length data.
askRaw(bytes)
	Ask the device for a variable length data using raw encoded command.
sendSimpleCommand(address, command)
	Send a nullary command to the device.
sendByteCommand(address, command, argument)
	Send an unary command to the device.
sendWordCommand(address, command, argument)
	Send an unary command to the device.
sendData(address, bytes)
	Send variable length data to the device.

Attributes
----------
DONE : int
	"Success" result code
BUSY : int
	"The device is busy" result code
NONE : int
	"None" return code

Example
-------

>>> x = RS485("/dev/ttyUSB0", 115)

)";

	constexpr static const char* init_docstring = R"(
Create RS485 object

Parameters
----------
filenames : str
	The path to the device file.
baudrate : int
	Working baudrate in Kbps.

Example
-------

>>> x = RS485("/dev/ttyUSB0", 115)

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.
)";

	constexpr static const char* askByte_docstring = R"(
Ask the device for a byte of data.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.

Returns
-------
int
	The 8-bit unsigned integer value associated with the command id.

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.

See Also
--------
askWord, askLong
)";

	constexpr static const char* askWord_docstring = R"(
Ask the device for a word of data.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.

Returns
-------
int
	The 16-bit unsigned integer value associated with the command id.

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.

See Also
--------
askByte, askLong
)";

	constexpr static const char* askLong_docstring = R"(
Ask the device for a double word of data.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.

Returns
-------
int
	The 24-bit signed integer value associated with the command id.

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.

See Also
--------
askByte, askWord
)";

	constexpr static const char* askData_docstring = R"(
Ask the device for a variable length data.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.

Returns
-------
bytes
	The data associated with the command id.

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.
)";

	constexpr static const char* askRaw_docstring = R"(
Ask the device for a variable length data using raw encoded command.

You are discouraged to use this function in your code. The only case when the
function can be useful is implementing tools similar to ``lmox``.

Parameters
----------
bytes : bytes
	The bytes to be send to the device. The bytes must be in a correct
	procotol format, including the device address and the command id. The SLIP
	encoding are performed by the library.

Returns
-------
bytes
	The data associated with the request.

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.
)";

	constexpr static const char* sendSimpleCommand_docstring = R"(
Send a nullary command to the device.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.

Returns
-------
int
	Result code:
		- RS485.DONE = 0
		- RS485.BUSY = 1
		- RS485.NONE = 2

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.

See Also
--------
sendByteCommand, sendWordCommand
)";

	constexpr static const char* sendByteCommand_docstring = R"(
Send an unary command to the device.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.
argument : int
	The argument for the command, 8-bit unsigned integer.

Returns
-------
int
	Result code:
		- RS485.DONE = 0
		- RS485.BUSY = 1
		- RS485.NONE = 2

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.

See Also
--------
sendSimpleCommand, sendWordCommand
)";

	constexpr static const char* sendWordCommand_docstring = R"(
Send an unary command to the device.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
command : int
	The command id, 8-bit unsigned integer.
argument : int
	The argument for the command, 16-bit unsigned integer.

Returns
-------
int
	Result code:
		- RS485.DONE = 0
		- RS485.BUSY = 1
		- RS485.NONE = 2

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.

See Also
--------
sendSimpleCommand, sendByteCommand
)";

	constexpr static const char* sendData_docstring = R"(
Send variable length data to the device.

Parameters
----------
address : int
	The device address, 8-bit unsigned integer.
bytes : bytes
	The data to be sent to the device.

Returns
-------
int
	Result code:
		- RS485.DONE = 0
		- RS485.BUSY = 1
		- RS485.NONE = 2

Raises
------
RuntimeError
	An underlying C++ exception occured during the function call.
)";

private:
	std::unique_ptr<BaseRS485> impl_;
};

constexpr const char* rs485::docstring;
constexpr const char* rs485::init_docstring;
constexpr const char* rs485::askByte_docstring;
constexpr const char* rs485::askWord_docstring;
constexpr const char* rs485::askLong_docstring;
constexpr const char* rs485::askData_docstring;
constexpr const char* rs485::askRaw_docstring;
constexpr const char* rs485::sendSimpleCommand_docstring;
constexpr const char* rs485::sendByteCommand_docstring;
constexpr const char* rs485::sendWordCommand_docstring;
constexpr const char* rs485::sendData_docstring;


PYBIND11_MODULE(pycmox, m)
{
	py::register_exception<BaseRS485::ErrFatal>(m, "ErrFatal", PyExc_RuntimeError);
	py::register_exception<BaseRS485::ErrDriver>(m, "ErrDriver", PyExc_RuntimeError);
	py::register_exception<BaseRS485::ErrSignal>(m, "ErrSignal", PyExc_RuntimeError);

	{
	auto in_RS485 = py::class_<rs485>(m, "RS485", rs485::docstring)
		.def(py::init<std::string, int>(), rs485::init_docstring, py::arg("filename"), py::arg("baudrate"))
		.def("askByte", &rs485::askByte, rs485::askByte_docstring, py::arg("address"), py::arg("command"))
		.def("askWord", &rs485::askWord, rs485::askWord_docstring, py::arg("address"), py::arg("command"))
		.def("askLong", &rs485::askLong, rs485::askLong_docstring, py::arg("address"), py::arg("command"))
		.def("askData", &rs485::askData, rs485::askData_docstring, py::arg("address"), py::arg("command"))
		.def("askRaw",  &rs485::askRaw,  rs485::askRaw_docstring,  py::arg("bytes"))
		.def("sendSimpleCommand", &rs485::sendSimpleCommand, rs485::sendSimpleCommand_docstring, py::arg("address"), py::arg("command"))
		.def("sendByteCommand",   &rs485::sendByteCommand,   rs485::sendByteCommand_docstring,   py::arg("address"), py::arg("command"), py::arg("argument"))
		.def("sendWordCommand",   &rs485::sendWordCommand,   rs485::sendWordCommand_docstring,   py::arg("address"), py::arg("command"), py::arg("argument"))
		.def("sendData", &rs485::sendData, rs485::sendData_docstring, py::arg("address"), py::arg("bytes"))
		;

	in_RS485.attr("DONE") = static_cast<int>(BaseRS485::DONE);
	in_RS485.attr("BUSY") = static_cast<int>(BaseRS485::BUSY);
	in_RS485.attr("NONE") = static_cast<int>(BaseRS485::NONE);
	}
}
