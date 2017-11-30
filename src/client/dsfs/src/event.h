#ifndef DSFS_EVENT_H
#define DSFS_EVENT_H

#include <pthread.h>
#include <zmq.hpp>

namespace dsfs
{
    class Context;

    class EventInterface {
    public:
        enum event_type
        {
            EVENT_OPEN = 1,
            EVENT_WRITE,
            EVENT_READ,
            EVENT_RELEASE,
            EVENT_UNLINK,
            EVENT_RMDIR,
            EVENT_RENAME,
        };
        explicit EventInterface(Context *context, const std::string& event_addr);
        void sendFileSystemInfo(const std::string& volumeKey);
        void notify(event_type event, const char *path);
        ~EventInterface();
    private:
        zmq::context_t _inter_context;
        zmq::socket_t _socket;
        mutable pthread_mutex_t _event_mutex;
    private:
        Context *_context;
    };
}

#endif //DSFS_EVENT_H
