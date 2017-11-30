#ifndef DSFS_CONTEXT_H_H
#define DSFS_CONTEXT_H_H

#include <zmq.hpp>
#include "Context.h"
#include "fuse.h"

#include "event.h"

namespace dsfs
{
    class EventInterface;

    class Context : public encfs::EncFS_Context
    {
    public:
        explicit Context(const std::string& event_addr);
        ~Context();
        EventInterface *event();
    private:
        EventInterface _event;
    };

    static Context *get_context() {
        return (Context*)fuse_get_context()->private_data;
    }
};

#endif //DSFS_CONTEXT_H_H
