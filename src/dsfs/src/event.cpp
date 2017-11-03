#include <pthread.h>
#include <zmq.hpp>

#include "event.h"
#include "context.h"

#include "Mutex.h"
#include "FileNode.h"
#include "DirNode.h"


using namespace dsfs;

EventInterface::EventInterface(Context *context, const std::string& event_addr)
    : _context(context),
      _inter_context(1),
      _socket(_inter_context, ZMQ_PAIR)
{
    _socket.bind(event_addr);

    // _socket.setsockopt(ZMQ_SNDTIMEO, 1000);
    // _socket.setsockopt(ZMQ_RCVTIMEO, 1000);

    pthread_mutex_init(&_event_mutex, nullptr);
}

EventInterface::~EventInterface()
{
    pthread_mutex_destroy(&_event_mutex);
    LOG(INFO) << "Event interface is down";
}

void EventInterface::notify(event_type event, const char *path)
{
    /// LOG(INFO) << "[" << pthread_self() << "] " << "Sending event " << event << " for " << path;

    int err = 0;
    auto root = _context->getRoot(&err);

    if(err)
    {
        LOG(ERROR) << "Failed to get filesystem root for event reporting";
        return;
    }

    encfs::Lock lock(_event_mutex);

    try {
        zmq::message_t msg(&event, sizeof(event));

        if(!_socket.send(msg, ZMQ_SNDMORE))
            throw zmq::error_t();

        std::string name = path;
        std::string cipher = root->cipherPath(path);

        msg.rebuild(name.c_str(), name.length());
        if(!_socket.send(msg, ZMQ_SNDMORE))
            throw zmq::error_t();

        msg.rebuild(cipher.c_str(), cipher.length());
        if(!_socket.send(msg))
            throw zmq::error_t();

        // if(!_socket.recv(&msg))
            // throw zmq::error_t();
    }
    catch(zmq::error_t& err)
    {
        LOG(ERROR) << "Interprocess error, cannot send event to sync service!";
    }
}
