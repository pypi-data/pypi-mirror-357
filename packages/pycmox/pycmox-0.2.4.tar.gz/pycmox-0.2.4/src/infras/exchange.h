#ifndef _EXCHANGE_H
#define _EXCHANGE_H
#include <stdexcept>
#include <sstream>
#include <vector>
#include <sys/time.h>
#include <termios.h>

const unsigned int IO_BUFF_SIZE = 128; // user/system buffer size

class RS485command {
protected:
    int cm;
public:
    RS485command( int code ) : cm(code) {}
    RS485command operator=( int code ){ return RS485command(code); }
    operator char() const {return (char)cm; }
};

class SComm : public RS485command {
public:
    SComm(int code) : RS485command(code) {}
};

class SByte : public RS485command {
public:
    SByte(int code) : RS485command(code) {}
};

class SWord : public RS485command {
public:
    SWord(int code) : RS485command(code) {}
};

class SData : public RS485command {
public:
    SData(int code) : RS485command(code) {}
};

class AByte : public RS485command {
public:
    AByte(int code) : RS485command(code) {}
};

class AWord : public RS485command {
public:
    AWord(int code) : RS485command(code) {}
};

class ALong : public RS485command {
public:
    ALong(int code) : RS485command(code) {}
};

class AData : public RS485command {
public:
    AData(int code) : RS485command(code) {}
};

class BaseRS485 {
protected:
    unsigned char strcomm[IO_BUFF_SIZE];
    unsigned char strread[IO_BUFF_SIZE];
    unsigned char strdata[IO_BUFF_SIZE];
    unsigned int packet_number;
    unsigned int errors_number;
    unsigned int extranum;
    unsigned int cycl_prevs;
    size_t rsize;
    std::string logstr_;
private:
    BaseRS485(const BaseRS485&);
    BaseRS485& operator=(const BaseRS485&);
public:
    enum com_stat {DONE, BUSY, NONE };
    class ErrFatal : public std::runtime_error {
    public:
        ErrFatal( const std::string& mess ) : std::runtime_error(mess) {}
    };
    class ErrDriver : public std::runtime_error {
    public:
        ErrDriver( const std::string& mess ) : std::runtime_error(mess) {}
    };
    class ErrSignal : public std::runtime_error {
    public:
        ErrSignal( const std::string& mess ) : std::runtime_error(mess) {}
    };
protected:
    class RS485log {
    private:
        std::ostringstream s;
        BaseRS485* ptr_;
    private:
        friend class BaseRS485;
        static void set_logstr(BaseRS485* ptr, const std::string& str);
    public:
        RS485log(const unsigned char *inp,  const int nbyte, BaseRS485* ptr);
        ~RS485log();
        void log(const std::string& t);
        void log(unsigned char *out, const int n);
    };
    friend void RS485log::set_logstr(BaseRS485* ptr, const std::string& str);
private:
    virtual int transaction(const unsigned char*, std::size_t, unsigned char*, std::size_t) = 0;
public:
    BaseRS485();
    virtual ~BaseRS485() = 0;
    int askByte( unsigned int, const AByte);
    int askWord( unsigned int, const AWord);
    int askLong( unsigned int, const ALong);
    std::vector<unsigned char> askData( unsigned int, const AData);
    std::vector<unsigned char> askRaw(const std::vector<unsigned char>& raw);
    com_stat sendSimpleCommand( unsigned int, const SComm);
    com_stat sendByteCommand( unsigned int, const SByte, char b);
    com_stat sendWordCommand( unsigned int, const SWord, short w);
    com_stat sendData( unsigned int, const SData, const std::vector<unsigned char>& );
    inline unsigned int stat_packets() const { return packet_number; }
    inline unsigned int stat_errors() const { return errors_number; }
    virtual std::string protocol() = 0;
    virtual int readData(unsigned int&, unsigned int&, unsigned short*, std::size_t) = 0;
    virtual void resetData();
    inline const std::string& logstr() const { return logstr_; }
};

#ifndef NO_RS485_LEGACY
class RS485LegacyImpl: public BaseRS485 {
private:
    int fd_;
private:
    virtual int transaction(const unsigned char*, std::size_t, unsigned char*, std::size_t);
public:
    RS485LegacyImpl(int fd, int baudrate);
    ~RS485LegacyImpl();
    virtual std::string protocol();
    virtual int readData(unsigned int&, unsigned int&, unsigned short*, std::size_t);
    virtual void resetData();
};
#endif // NO_RS485_LEGACY

class RS485TTYImpl: public BaseRS485 {
private:
    struct termios old_termios_;
    int fd_;
private:
    virtual int transaction(const unsigned char*, std::size_t, unsigned char*, std::size_t);
public:
    RS485TTYImpl(int fd, int baudrate);
    ~RS485TTYImpl();
    virtual std::string protocol();
    virtual int readData(unsigned int&, unsigned int&, unsigned short*, std::size_t);
};

class RS485ImplFactory {
private:
    std::string device_;
    int baudrate_;
private:
#ifndef NO_RS485_LEGACY
    static bool is_legacy(int fd);
#endif // NO_RS485_LEGACY
    static bool is_tty(int fd);
public:
    RS485ImplFactory(const std::string& device, int baudrate = 0);
    BaseRS485* create() const;
};

class RSTimer {
    struct itimerval old;
    struct itimerval end;
    static bool expired;
public:
    RSTimer( double );
    ~RSTimer();
    bool out() { return expired; }
private:
     static void catch_alarm(int sig);
};

#endif
