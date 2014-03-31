#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "MOOS/libMOOS/Comms/MOOSMsg.h"
#include "MOOS/libMOOS/Comms/MOOSCommClient.h"
#include "MOOS/libMOOS/Comms/MOOSAsyncCommClient.h"

namespace bp = boost::python;
/*
struct World
{
    void set(std::string msg) { this->msg = msg; }
    std::string greet() { return msg; }
    std::string msg;

    bool f(int j){j=8;return true;};
    bool f(int j,int k){j=8;k=9;return true;};

    std::string call_wrap(bp::object & func)
    {
        PyGILState_STATE gstate = PyGILState_Ensure();

        bp::object result = func();

        PyGILState_Release(gstate);

        return bp::extract<std::string>(result);
    }

};


std::string call_wrap(bp::object & func)
{
    bp::object result = func();
    return bp::extract<std::string>(result);
}*/

namespace MOOS
{


class AsyncCommsWrapper : public MOOS::MOOSAsyncCommClient
{
private:
    typedef MOOSAsyncCommClient BASE;
public:

    bool Run(const std::string & sServer, int Port, const std::string & sMyName)
    {
        return BASE::Run(sServer,Port,sMyName,0);//Comms Tick not used in Async version
    }


    std::vector<CMOOSMsg> FetchMailAsVector()
    {
        std::vector<CMOOSMsg> v;
        MOOSMSG_LIST M;
        if(Fetch(M))
        {
            std::copy(M.begin(),M.end(),std::back_inserter(v));
        }

        return v;
    }


    bool NotifyBinary(const std::string& sKey,const std::string & sData, double dfTime)
    {
        CMOOSMsg M(MOOS_NOTIFY,sKey, sData.size(),(void *) sData.data(), dfTime);
        return BASE::Post( M );
    }


    static bool on_connect_delegate(void * pParam)
    {
        MOOS::AsyncCommsWrapper * pMe = static_cast<MOOS::AsyncCommsWrapper*> (pParam);
        return pMe->on_connect();
    }
    bool SetOnConnectCallback(bp::object  func)
    {
        BASE:SetOnConnectCallBack(on_connect_delegate,this);
        on_connect_object_ = func;
        return true;
    }
    bool on_connect()
    {
        PyGILState_STATE gstate = PyGILState_Ensure();
        bp::object result = on_connect_object_();
        PyGILState_Release(gstate);
        return bp::extract<bool>(result);
    }


    bool SetOnMailCallback(bp::object  func)
    {
        BASE:SetOnMailCallBack(on_mail_delegate,this);
        on_mail_object_ = func;
        return true;
    }

    static bool on_mail_delegate(void * pParam)
    {
        MOOS::AsyncCommsWrapper * pMe = static_cast<MOOS::AsyncCommsWrapper*> (pParam);
        return pMe->on_mail();
    }

    bool on_mail()
    {
        PyGILState_STATE gstate = PyGILState_Ensure();
        bp::object result = on_mail_object_();
        PyGILState_Release(gstate);
        return bp::extract<bool>(result);
    }

    static bool active_queue_delegate(CMOOSMsg & M, void* pParam)
    {
        MeAndQueue * maq = static_cast<MeAndQueue*> (pParam);
        return maq->me_->OnQueue(M,maq->queue_name_);
    }

    bool OnQueue(CMOOSMsg & M, const std::string & sQueueName)
    {
        std::map<std::string, MeAndQueue*>::iterator q ;

        {
            MOOS::ScopedLock L(queue_api_lock_);
            q = active_queue_details_.find(sQueueName);
            if(q==active_queue_details_.end())
                return false;
        }

        PyGILState_STATE gstate = PyGILState_Ensure();
        bp::object result = q->second->func_(M);
        PyGILState_Release(gstate);
        return bp::extract<bool>(result);

    }

    virtual bool AddActiveQueue(const std::string & sQueueName,
                                bp::object func,
                    void * pYourParam )
    {
        MOOS::ScopedLock L(queue_api_lock_);

        MeAndQueue* maq = new MeAndQueue;
        maq->me_=this;
        maq->queue_name_=sQueueName;
        maq->func_=func;

        active_queue_details_[sQueueName]=maq;
        return BASE::AddActiveQueue(sQueueName,active_queue_delegate,maq);

    }

struct MeAndQueue
{
    AsyncCommsWrapper* me_;
    std::string queue_name_;
    bp::object func_;
};

private:
    bp::object  on_connect_object_;
    bp::object  on_mail_object_;
    std::map<std::string, MeAndQueue*> active_queue_details_;
    CMOOSLock queue_api_lock_;


};
};

typedef std::vector<CMOOSMsg> MsgVector;

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(f_overloads, f, 1, 2);
BOOST_PYTHON_FUNCTION_OVERLOADS(time_overloads, MOOSTime, 0, 1);
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(notify_overloads_2_3, Notify, 2,3);
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(notify_overloads_3_4, Notify, 3,4);

BOOST_PYTHON_MODULE(pymoos)
{
    PyEval_InitThreads();

    bp::class_<CMOOSMsg>("moos_msg")
            .def("time", &CMOOSMsg::GetTime)
            .def("trace", &CMOOSMsg::Trace)

            .def("name", &CMOOSMsg::GetKey)
            .def("key", &CMOOSMsg::GetKey)
            .def("is_name", &CMOOSMsg::IsName)

            .def("is_double", &CMOOSMsg::IsDouble)
            .def("double", &CMOOSMsg::GetDouble)
            .def("double_aux", &CMOOSMsg::GetDoubleAux)

            .def("is_string", &CMOOSMsg::IsString)
            .def("string", &CMOOSMsg::GetString)

            .def("is_binary", &CMOOSMsg::IsBinary)
            .def("binary_data",&CMOOSMsg::GetString)
            .def("binary_data_size", &CMOOSMsg::GetBinaryDataSize)
            .def("mark_as_binary", &CMOOSMsg::MarkAsBinary)
            ;

    bp::class_<MsgVector>("moos_msg_list")
            .def(bp::vector_indexing_suite<MsgVector>() )
            ;


    bp::class_<CMOOSCommObject >("base_comms_object",bp::no_init);

    bp::class_<CMOOSCommClient, bp::bases<CMOOSCommObject>, boost::noncopyable >("base_sync_comms",bp::no_init)
        .def("register", static_cast< bool (CMOOSCommClient::*)(const std::string& ,double) > (&CMOOSCommClient::Register))
        .def("register", static_cast< bool (CMOOSCommClient::*)(const std::string&,const std::string&,double) > (&CMOOSCommClient::Register))

        .def("notify", static_cast< bool (CMOOSCommClient::*)(const std::string&,const std::string&,double) > (&CMOOSCommClient::Notify),notify_overloads_2_3())
        .def("notify", static_cast< bool (CMOOSCommClient::*)(const std::string&,const std::string&,const std::string&,double) > (&CMOOSCommClient::Notify),notify_overloads_2_3())

        .def("notify", static_cast< bool (CMOOSCommClient::*)(const std::string&,const char *,double) > (&CMOOSCommClient::Notify))
        .def("notify", static_cast< bool (CMOOSCommClient::*)(const std::string&,const char *,const std::string&,double) > (&CMOOSCommClient::Notify))

        .def("notify", static_cast< bool (CMOOSCommClient::*)(const std::string&,double,double) > (&CMOOSCommClient::Notify))
        .def("notify", static_cast< bool (CMOOSCommClient::*)(const std::string&,double,const std::string&,double) > (&CMOOSCommClient::Notify))

        .def("get_community_name", &CMOOSCommClient::GetCommunityName)
        .def("get_moos_name", &CMOOSCommClient::GetMOOSName)

        .def("is_connected", &CMOOSCommClient::IsConnected)
        .def("wait_until_connected", &CMOOSCommClient::WaitUntilConnected)

        .def("get_description", &CMOOSCommClient::GetDescription)
        .def("close", &CMOOSCommClient::Close)

        .def("get_published", &CMOOSCommClient::GetPublished)
        .def("get_registered", &CMOOSCommClient::GetRegistered)

        .def("is_registered_for", &CMOOSCommClient::IsRegisteredFor)
        .def("is_running", &CMOOSCommClient::IsRunning)

        .def("is_asynchronous", &CMOOSCommClient::IsAsynchronous)

        .def("get_number_of_unread_messages", &CMOOSCommClient::GetNumberOfUnreadMessages)
        .def("get_number_of_unsent_messages", &CMOOSCommClient::GetNumberOfUnsentMessages)

        .def("get_number_bytes_sent", &CMOOSCommClient::GetNumBytesSent)
        .def("get_number_bytes_read", &CMOOSCommClient::GetNumBytesReceived)

        .def("get_number_messages_sent", &CMOOSCommClient::GetNumMsgsSent)
        .def("get_number_message_read", &CMOOSCommClient::GetNumMsgsReceived)

        .def("set_comms_control_timewarp_scale_factor", &CMOOSCommClient::SetCommsControlTimeWarpScaleFactor)
        .def("get_comms_control_timewarp_scale_factor", &CMOOSCommClient::GetCommsControlTimeWarpScaleFactor)


        .def("set_quiet", &CMOOSCommClient::SetQuiet)
        .def("do_local_time_correction", &CMOOSCommClient::DoLocalTimeCorrection)

        .def("set_verbose_debug", &CMOOSCommClient::SetVerboseDebug)
        .def("set_comms_tick", &CMOOSCommClient::SetCommsTick)


        ;


    bp::class_<MOOS::MOOSAsyncCommClient, bp::bases<CMOOSCommClient>, boost::noncopyable >("base_async_comms",bp::no_init)
            .def("run", &MOOS::MOOSAsyncCommClient::Run)
            ;

    //this is the one to use
    bp::class_<MOOS::AsyncCommsWrapper, bp::bases<MOOS::MOOSAsyncCommClient>, boost::noncopyable >("comms")
              .def("run", &MOOS::AsyncCommsWrapper::Run)
              .def("fetch", &MOOS::AsyncCommsWrapper::FetchMailAsVector)

              .def("set_on_connect_callback", &MOOS::AsyncCommsWrapper::SetOnConnectCallback)
              .def("set_on_mail_callback", &MOOS::AsyncCommsWrapper::SetOnMailCallback)

              .def("notify_binary", &MOOS::AsyncCommsWrapper::NotifyBinary)

              .def("add_active_queue", &MOOS::AsyncCommsWrapper::AddActiveQueue)

              ;


/*
    bp::class_<World>("World")
        .def("greet", &World::greet)
        .def("set", &World::set)
        .def("call", &World::call_wrap)
        .def("f",static_cast< bool (World::*)(int) > (&World::f) )
        .def("f",static_cast< bool (World::*)(int,int) > (&World::f) );

    bp::def("call", &call_wrap);*/

    bp::def("time",&MOOSTime,time_overloads());
    bp::def("local_time",&MOOSLocalTime,time_overloads());
    bp::def("is_little_end_in",&IsLittleEndian);

}

