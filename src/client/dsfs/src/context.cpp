#include <zmq.hpp>

#include "event.h"
#include "context.h"

using namespace dsfs;

Context::Context(const std::string& event_addr) :
    EncFS_Context(),
    _event(this, event_addr)
{}

EventInterface *Context::event()
{
    return &_event;
}

Context::~Context()
{
    LOG(INFO) << "Context Destroyed";
}

