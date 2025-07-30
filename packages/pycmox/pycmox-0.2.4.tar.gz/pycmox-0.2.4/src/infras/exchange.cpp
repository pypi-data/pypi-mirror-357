#include <sys/ioctl.h>
#include <sys/poll.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>
#include <sstream>
#include <cassert>
#include <cerrno>
#include <cstring>
#include <sys/time.h>
#include <vector>
#include <map>
#include <iostream>
#include <iomanip>
#include <signal.h>
#include <cmath>

#ifndef NO_RS485_LEGACY
#include <linux/rs485/mcua.h>
#include <linux/rs485/rserrno.h>
#else
#define SignalPKL   0x81
#define SignalPBO   0x82
#define SignalEER   0x83
#define SignalDSC   0x84
#define SignalCOL   0x86
#define SignalUND   0x90
#define SignalACK   0x87
#define SignalNAK   0x96
#define SignalNOD   0xA5
#define SignalACN   0xB4
#define SignalACY   0xC3
#define SignalACW   0xD2
#define SignalSINC  0xE1
#define SignalDNG   0xF0
#endif // NO_RS485_LEGACY

#include <exchange.h>

#include <unistd.h>                 // write, usleep, close

const int MAXRETRY  = 3;            // Maximal number of transaction attempts
const int MAX_PACKET_SIZE = 32;     // Maximal packet size
const unsigned char MASK_CNT_PACKET = 0x60;
const unsigned char MASK_ADR_PACKET = 0x1f;
const int SIGNAL_BASE = 0x80;

const int ACK = SignalACK;
const int NAK = SignalNAK;
const int NOD = SignalNOD;
const int ACN = SignalACN;
const int ACY = SignalACY;
const int ACW = SignalACW;
const int SINC= SignalSINC;
const int DNG = SignalDNG;
const int PKL = SignalPKL;
const int PBO = SignalPBO;
const int DSC = SignalDSC;
const int COL = SignalCOL;
const int EER = SignalEER;
const int UND = SignalUND;

const int END =     0xC0 ;           // indicates end of frame
const int ESC =     0xDB ;           // indicates byte stuffing
const int ESC_END = 0xDC ;           // ESC ESC_END means END 'data'
const int ESC_ESC = 0xDD ;           // ESC ESC_ESC means ESC 'data'

namespace {
    inline unsigned char low(short i) {
        return (unsigned char)(i&0x00ff);
    }
    inline unsigned char high(short i) {
        return (unsigned char)((i&0xff00)>>8);
    }
}

enum { INFO_SIG, LOOP_SIG };

struct Signl {
    int stype;
    std::string abbr;
    std::string text;
    Signl(const int st, const std::string& a, const std::string& t)
          : stype(st), abbr(a), text(t) {};
    Signl() {};
};

namespace Signal {
    const std::string& abbrev( int code);
    const std::string& message( int code);
    int type( int code);
    typedef std::pair< int, struct Signl> PAIR;
    PAIR p[] = {
        PAIR( ACK, Signl(INFO_SIG, "ACK", "Successful data transmission")),
        PAIR( NOD, Signl(INFO_SIG, "NOD", "Required data are not ready")),
        PAIR( ACN, Signl(INFO_SIG, "ACN", "This command does not exist")),
        PAIR( ACY, Signl(INFO_SIG, "ACY", "Acknowledgement of existing command")),
        PAIR( ACW, Signl(INFO_SIG, "ACW", "Command can't be executed now")),
        PAIR( DSC, Signl(LOOP_SIG, "DSC", "Module doesn't respond")),
        PAIR( NAK, Signl(LOOP_SIG, "NAK", "Broken packet was received")),
        PAIR( COL, Signl(LOOP_SIG, "COL", "Transmission error or packets collision")),
        PAIR( UND, Signl(LOOP_SIG, "UND", "Unexpected data instead of signal ")),
        PAIR( EER, Signl(LOOP_SIG, "EER", "General exchange error"))
    };
    std::map< int, Signl> sg( p, p + sizeof(p)/sizeof(p[0]));
}

int Signal::type( int code) {
    return (sg.find(code) == sg.end())? sg[EER].stype : sg[code].stype;
}

const std::string& Signal::abbrev( int code) {
    return (sg.find(code) == sg.end())? sg[EER].abbr : sg[code].abbr;
}

const std::string& Signal::message( int code) {
    return (sg.find(code) == sg.end())? sg[EER].text : sg[code].text;
}

namespace {
#ifndef NO_RS485_LEGACY
    const std::string RS_strerror(int errnum) {
        switch(errnum) {
            case ERSNODEVICE    :
            case ENOENT         : return "No RS485 device";
            case ERSNOPORT      : return "No this port";
            case ERSNOINTERFACE : return "No RS485 interface";
            case ENODEV         :
            case ERSNODRIVER    : return "No RS485 driver";
            case ERSBUSY        : return "RS485 device is busy";
            case ERSSHUTDOWN    : return "Device is off or disconnected";
            case ERSISATMOUT    : return "RS485 ISA time out";
            case ERSNOCONVREPLY : return "No reply from RS485 converter";
            case ERSFRAME       : return "RS485 frame error";
            case ERSFIFOVERFLOW : return "RS485 FIFO overflow";
            case ERSNOIOCTL     : return "RS485: no such ioctl command";
            default             : if( errnum < ERSBASE ) return std::strerror(errnum);
                                  return "Unknown RS485 error";
        }
    }
#endif // NO_RS485_LEGACY

    long baudrate_flag( int r ) {
        long flags = 0;
        switch( (int)(115200*rint(r/115.200)) ) {
            case 115200:
                flags = B115200;
                break;
            case 230400:
                flags = B230400;
                break;
            case 460800:
                flags = B460800;
                break;
            case 921600:
                flags = B921600;
                break;
            default:
                flags = -1;
        }
        return flags;
    }

    unsigned char crc(const unsigned char *buf, size_t size) {
        // calculation of the control sum (crc),  return crc,
        // *buf - poiter to data,  size - buffer size
        const unsigned short divisor = 0x700;
        unsigned short acc = 0;
        while (size--) {
            acc |= *(buf++);
            for (size_t i = 0; i < 8; i++)
		acc = acc & 0x8000 ? (acc << 1)^divisor : acc << 1;
        }
        for (size_t i = 0; i < 8; i++)
            acc = acc & 0x8000 ? (acc << 1)^divisor : acc << 1;
        acc = acc >> 8;
        return (unsigned char)acc;
    }

    int slip_esc( const unsigned char *s, unsigned char *d, int len ) {
        unsigned char* ptr;
        unsigned char c;
        ptr = d;
            // For each byte in the packet, send the appropriate  character
            // sequence, according to the SLIP protocol.
        while ( len-- > 0) {
            switch ( c = *s++ ) {
            case END:
                *ptr++ = ESC;
                *ptr++ = ESC_END;
                break;
            case ESC:
                *ptr++ = ESC;
                *ptr++ = ESC_ESC;
                break;
            default:
                *ptr++ = c;
                break;
            }
        }
        *ptr++ = END;
        return ptr - d;
    }

    int slip_unesc( unsigned char *s, unsigned char *d, int len ) {
        unsigned char* ptr = d;
        unsigned char c;
        int was_esc = 0;
        ptr = d;
        while ( len-- > 0 ) {
            switch( c = *s++ ) {
            case END:
//                break;        Checked with repeatetive packets
                return ptr - d;
            case ESC:
                was_esc = 1;
                break;
            case ESC_ESC:
                if( was_esc ) {
                    *ptr++ = ESC;
                    was_esc  = 0;
                } else *ptr++ = c;
                break;
            case ESC_END:
                if( was_esc ) {
                    *ptr++ = END;
                    was_esc  = 0;
                } else *ptr++ = c;
                break;
            default:
                *ptr++ = c;
            }
        }
        return ptr - d;
    }
}

BaseRS485::RS485log::RS485log( const unsigned char *inp,  const int nbyte, BaseRS485* ptr ): ptr_(ptr) {
    s << std::hex << std::fixed << std::setfill('0');
    for( int i=0; i < nbyte; i++ ) s << std::setw(2) << (int)inp[i] << " ";
    s << "<- ";
}
BaseRS485::RS485log::~RS485log() {
    set_logstr(ptr_, std::string("-> ") + s.str());
}
void BaseRS485::RS485log::log( const std::string& t ) {
    s << t << " ";
}
void BaseRS485::RS485log::log( unsigned char *out, const int n ) {
    for( int i=0; i < n; i++ ) s << std::setw(2) << (int)out[i] << " ";
}
void BaseRS485::RS485log::set_logstr(BaseRS485* ptr, const std::string& str) {
    ptr->logstr_ = str;
}

BaseRS485::BaseRS485(): packet_number(0), errors_number(0), extranum(0), cycl_prevs(0), rsize(0) {
}
BaseRS485::~BaseRS485() {
}
void BaseRS485::resetData() {
    extranum = 0;
    cycl_prevs = 0;
    rsize = 0;
}

int BaseRS485::askByte( unsigned int module, const AByte command ) {
    int nsent  = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( ret != 1 ) throw ErrSignal( Signal::abbrev(ret) );
    return (int)(*strread);
}

int BaseRS485::askWord( unsigned int module, const AWord command ) {
    int nsent = 0;
    int avalue = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( ret != 2 ) throw ErrSignal( Signal::abbrev(ret) );
    memcpy( (char*)&avalue, strread, 2 );
    return avalue ;
}

int BaseRS485::askLong( unsigned int module, const ALong command ) {
    int nsent = 0;
    int avalue = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( ret != 3 ) throw ErrSignal( Signal::abbrev(ret) );
    strread[3] = (strread[2] > 0x7f ? 0xff : 0);
    memcpy( (char*)&avalue, strread, 4 );
    return avalue;
}

std::vector<unsigned char> BaseRS485::askData( unsigned int module, const AData command ) {
    int nsent = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( ret < MAX_PACKET_SIZE ) return std::vector<unsigned char>( strread, strread+ret );
    if( ret != NOD ) throw ErrSignal( Signal::abbrev(ret) );
    return std::vector<unsigned char>();
}

std::vector<unsigned char> BaseRS485::askRaw(const std::vector<unsigned char>& raw) {
    memcpy(strcomm, &raw[0], raw.size());
    int ret = transaction(strcomm, raw.size(), strread, sizeof(strread));
    if( ret < MAX_PACKET_SIZE ) return std::vector<unsigned char>( strread, strread+ret );
    throw ErrSignal( Signal::abbrev(ret) );
}

BaseRS485::com_stat BaseRS485::sendSimpleCommand( unsigned int module, const SComm command) {
    int nsent = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( (ret == ACY) || (ret == ACK) ) return DONE;
    if( ret != ACW ) {
            throw ErrSignal( Signal::abbrev(ret) );
    }
    return BUSY;
}

BaseRS485::com_stat BaseRS485::sendByteCommand( unsigned int module, const SByte command, char arg) {
    int nsent = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    strcomm[nsent++] = arg;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( (ret == ACY) || (ret == ACK) ) return DONE;
    if( ret != ACW) throw ErrSignal( Signal::abbrev(ret) );
    return BUSY;
}

BaseRS485::com_stat BaseRS485::sendWordCommand( unsigned int module, const SWord command, short arg) {
    int nsent = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)command;
    strcomm[nsent++] = low( arg );
    strcomm[nsent++] = high( arg );
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( (ret == ACY) || (ret == ACK) ) return DONE;
    if(ret != ACW) throw ErrSignal( Signal::abbrev(ret) );
    return  BUSY;
}

BaseRS485::com_stat BaseRS485::sendData( unsigned int module, const SData length, const std::vector<unsigned char>& data) {
    int nsent = 0;
    strcomm[nsent++] = (char)module;
    strcomm[nsent++] = (char)length;
    memcpy(strcomm+2, &data[0], length );
    nsent = length+2;
    int ret = transaction(strcomm, nsent, strread, sizeof(strread));
    if( (ret == ACY) || (ret == ACK) ) return DONE;
    if(ret != ACW) throw ErrSignal( Signal::abbrev(ret) );
    return BUSY;
}

#ifndef NO_RS485_LEGACY
int RS485LegacyImpl::transaction( const unsigned char *buffi, std::size_t nbyte, unsigned char *buffo, std::size_t) {
    int reply = 0;
    unsigned char temporal[IO_BUFF_SIZE];
    int attempt = MAXRETRY;
    packet_number++;
    if( nbyte > MAX_PACKET_SIZE ) throw ErrFatal( "Too long command. Why??" );
    RS485log scr( buffi, nbyte, this );
    RSTimer time = RSTimer( 1.0 );
    usleep(2000);
    while( attempt-- ) {
        memcpy( temporal, buffi, nbyte );
        reply = write( fd_, temporal, nbyte );
        if( time.out() ) throw ErrDriver( "RS driver timeout" );
        if( reply < 0 ) {
            errors_number++;
            scr.log(RS_strerror(errno));
            if( attempt == 0 ) throw ErrDriver( RS_strerror(errno) );
            usleep(4000);
            ioctl( fd_, RS_RESET );
            scr.log( " RESET " );
            continue;
        }
        if( reply <= MAX_PACKET_SIZE) {         // data, no Signal
            memcpy( buffo, temporal+1, --reply );
            scr.log( buffo, reply );
            return reply;
        }
        if( Signal::type(reply) == INFO_SIG ) { // info Signal
            scr.log( Signal::abbrev(reply));
            return reply;
        }
        errors_number++;
        scr.log( Signal::abbrev(reply));
        usleep(2000);
    }                   // loop Signal
    return reply;
}
RS485LegacyImpl::RS485LegacyImpl(int fd, int baudrate): BaseRS485(), fd_(fd) {
    char vers[32];
    if(ioctl(fd_, RS_GET_VERS, vers) < 0) {
        close(fd_);
        throw ErrFatal(RS_strerror(errno));
    }
    if(baudrate != 0 && ioctl(fd_, RS_SET_BAUDRATE, baudrate) < 0) {
        close(fd_);
        throw ErrFatal( "Unsupported exchange rate" );
    }
    logstr_ = std::string("Driver version ") + std::string(vers);
}
RS485LegacyImpl::~RS485LegacyImpl() {
    close(fd_);
}
std::string RS485LegacyImpl::protocol() {
    return "Legacy";
}
int RS485LegacyImpl::readData(unsigned int& from, unsigned int& numb, unsigned short *data, std::size_t) {
    static const int headlen = 4;
    int n_read_data = 0;
    int ret = 0;
    unsigned short pnum;
    if( ( n_read_data = read(fd_, strdata, IO_BUFF_SIZE ) ) ) {
        if( n_read_data < 0) throw ErrFatal( RS_strerror(errno) );
        if( n_read_data > headlen && !(( n_read_data - headlen )%2)) {
            ret = ( n_read_data - headlen )/2;          // The number of short words
            from = (unsigned int)(*(strdata+2));        // Sender address
            memcpy( &pnum, strdata + 3, 2 );            // The current packet number
            numb = pnum + extranum;
            if( pnum == 0xFFFF ) extranum += 0x10000;
            memcpy( data, strdata + headlen + 1, n_read_data - headlen );
        }
    }
    return ret;
}
void RS485LegacyImpl::resetData() {
    BaseRS485::resetData();
    if(ioctl(fd_, RS_FIFO_FLUSH) < 0) {
        ErrFatal(RS_strerror(errno));
    }
    if(ioctl(fd_, RS_BLNUMBER_RESET) < 0) {
        ErrFatal(RS_strerror(errno));
    }
}
#endif // NO_RS485_LEGACY

int RS485TTYImpl::transaction(const unsigned char *buffi, std::size_t nbyte, unsigned char *buffo, std::size_t buflen) {
    assert(2*MAX_PACKET_SIZE + 1 <= IO_BUFF_SIZE);
    assert(nbyte < MAX_PACKET_SIZE);

    const int recv_timeout = 10; // ms
    int ret = 0;
    RS485log scr(buffi, nbyte, this);
    unsigned char tmp_buf[IO_BUFF_SIZE];
    size_t tmp_buf_len = 0;
    unsigned char icrc = crc(buffi, nbyte);
    tmp_buf_len  = slip_esc(buffi, tmp_buf, nbyte);
    tmp_buf_len += slip_esc(&icrc, tmp_buf + tmp_buf_len - 1, 1) - 1;

    if (tcflush(fd_, TCIFLUSH) < 0)
        throw ErrFatal(strerror(errno));
    if (write(fd_, tmp_buf, tmp_buf_len) < 0)
        throw ErrFatal(strerror(errno));
    if (tcdrain(fd_) < 0)
        throw ErrFatal(strerror(errno));
    packet_number++;

    tmp_buf_len = 0;
    struct pollfd p;
    p.fd = fd_;
    p.events = POLLIN;
    while ((ret = poll(&p, 1, recv_timeout)) > 0) {
        int ret2 = read(fd_, tmp_buf + tmp_buf_len, IO_BUFF_SIZE - tmp_buf_len);
        if (ret2 < 0)
            throw ErrFatal(strerror(errno));
        else if (ret2 == 0)
            throw ErrFatal("Unexpected end of file");
        
        // skip single END (empty frame)
        while (tmp_buf_len == 0 && ret2 > 0 && *tmp_buf == (unsigned char)END) {
            memmove(tmp_buf, tmp_buf+1, --ret2);
        }

        unsigned char* ptrend = std::find(tmp_buf + tmp_buf_len, tmp_buf + tmp_buf_len + ret2, (unsigned char)END);
        if (ptrend == tmp_buf + tmp_buf_len + ret2)
            tmp_buf_len += ret2;
        else { 
            tmp_buf_len = ptrend - tmp_buf + 1;
            break;
        }
        if (tmp_buf_len >= IO_BUFF_SIZE) {
            scr.log( Signal::abbrev(EER));
            errors_number++;
            return EER;
        }
    }
    if (ret < 0)
        throw ErrFatal(strerror(errno));
    else if (ret == 0) {
        scr.log( Signal::abbrev(DSC));
        errors_number++;
        return DSC;
    }
    
    tmp_buf_len = slip_unesc(tmp_buf, tmp_buf, tmp_buf_len);
    assert(tmp_buf_len > 0);

    if (tmp_buf_len == 1 && *tmp_buf > SIGNAL_BASE) {
        scr.log( Signal::abbrev(*tmp_buf));
        return *tmp_buf;
    }
    if (crc(tmp_buf, tmp_buf_len) != 0) {
        scr.log( Signal::abbrev(EER));
        errors_number++;
        return EER;
    }
    tmp_buf_len -= 3;
    memcpy(buffo, tmp_buf+2, buflen < tmp_buf_len ? buflen : tmp_buf_len);
    scr.log(buffo, tmp_buf_len);
    return tmp_buf_len;
}
RS485TTYImpl::RS485TTYImpl(int fd, int baudrate): BaseRS485(), fd_(fd) {
    struct termios new_termios;
    if(fcntl(fd_, F_SETFL, 0) < 0) {
        close(fd_);
        throw ErrFatal(strerror(errno));
    }
    if(tcgetattr(fd_, &old_termios_) < 0) {
        close(fd_);
        throw ErrFatal(strerror(errno));
    };
    new_termios = old_termios_;
    cfmakeraw(&new_termios);
    if(cfsetspeed(&new_termios, baudrate_flag(baudrate)) < 0) {
        close(fd_);
        throw ErrFatal("Unsupported exchange rate");
    }
    new_termios.c_cc[VMIN]  = 0;
    new_termios.c_cc[VTIME] = 0;
    new_termios.c_cflag |= CREAD|CLOCAL;
    if(tcsetattr(fd_, TCSANOW, &new_termios) < 0) {
        close(fd_);
        throw ErrFatal(strerror(errno));
    }
}
RS485TTYImpl::~RS485TTYImpl() {
    tcsetattr(fd_, TCSANOW, &old_termios_);
    close(fd_);
}
std::string RS485TTYImpl::protocol() {
	return "SLIP/TTY";
}
int RS485TTYImpl::readData(unsigned int& from, unsigned int& numb, unsigned short *data, std::size_t buflen) {
    int n_read_data = 0;
    int ret = 0;
    int data_length = 0;
    ssize_t res = 0;
    unsigned char* pend;
    while( (res = read( fd_, strdata+rsize, sizeof(strdata)-rsize )) > 0 ) {
        if( res < 0 ) throw ErrFatal( strerror( errno ) );
        rsize += res;
        if( rsize > (unsigned int)MAX_PACKET_SIZE ) break;
    }
    if( rsize > 0 ) {
        for( pend = strdata+1; pend < strdata+rsize; pend++ ) {
            if( *pend  == END ) {
                n_read_data = pend - strdata + 1;
                data_length = slip_unesc( strdata, strread, n_read_data );
                rsize = rsize - n_read_data;
                if( rsize > 0 ) memmove( strdata, pend+1, rsize );
                if( crc( strread, data_length ) != 0 ) {
                    ret = EER;                              // For log Only
                    break;
                }
                ret = data_length - 3;
                from = (unsigned int) (*strread & MASK_ADR_PACKET);
                unsigned int cycl_num = (unsigned int) ((*strread & MASK_CNT_PACKET )/0x20);
                extranum += (cycl_num < cycl_prevs )?  (cycl_num+4) - cycl_prevs : cycl_num - cycl_prevs;
//                std::cerr << "cn= " << cycl_num << "  cn-cp= "  << cycl_prevs << " en= " << extranum << std::endl;
                cycl_prevs = cycl_num;
                numb = extranum;
                memcpy(data, strread+2, (std::size_t)ret < buflen ? (std::size_t)ret : buflen);
                ret = ret/2;
                break;
            }
        }
    }
    return ret;
}

RS485ImplFactory::RS485ImplFactory(const std::string& device, int baudrate): device_(device), baudrate_(baudrate) {
}
#ifndef NO_RS485_LEGACY
bool RS485ImplFactory::is_legacy(int fd) {
    /* Check for legacy: ask rs485 specific ioctl */
    char vers[32];
    if(ioctl(fd, RS_GET_VERS, vers) < 0) {
        return false;
    }
    return true;
}
#endif // NO_RS485_LEGACY
bool RS485ImplFactory::is_tty(int fd) {
    /* Check for tty: ask tcgetattr */
    struct termios tmp_termios;
    if(tcgetattr(fd, &tmp_termios) < 0) {
        return false;
    }
    return true;
}
BaseRS485* RS485ImplFactory::create() const {
    int fd = open(device_.c_str(), O_RDWR|O_NOCTTY);
    if(fd < 0) {
        throw BaseRS485::ErrFatal(strerror(errno));
    }
#ifndef NO_RS485_LEGACY
    if(is_legacy(fd)) {
        return new RS485LegacyImpl(fd, baudrate_);
    } else
#endif // NO_RS485_LEGACY
    if(is_tty(fd)) {
        return new RS485TTYImpl(fd, baudrate_);
    } else {
        close(fd);
        throw std::runtime_error("Device file is neither tty nor legacy rs485 device");
    }
    return 0;
}

bool RSTimer::expired = false;

void RSTimer::catch_alarm(int sig) {
    expired = true;
}

RSTimer::RSTimer( double in ){
    expired = false;
    end.it_interval.tv_usec = 0;
    end.it_interval.tv_sec = 0;
    end.it_value.tv_usec = (unsigned int)rint( 1000000*(in - floor(in)));
    end.it_value.tv_sec = (unsigned int)floor(in);
    if( setitimer( ITIMER_REAL, &end, &old) < 0 )
        throw BaseRS485::ErrFatal( "RS timer wasn't set" );
    else  {
        if( signal( SIGALRM, catch_alarm ) == SIG_ERR ) BaseRS485::ErrFatal( "Handler wasn't set" );
    }
}

RSTimer::~RSTimer(){
    expired = false;
    end.it_interval.tv_usec = 0;
    end.it_interval.tv_sec = 0;
    end.it_value.tv_usec = 0;
    end.it_value.tv_sec = 0;
    setitimer( ITIMER_REAL, &end, NULL );
}

