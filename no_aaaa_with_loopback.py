def init(id, cfg):
    return True

def deinit(id):
    return True

def inform_super(id, qstate, superqstate, qdata):
    return True

localhost_domains = [
    "localtest.me.",
    "lvh.me."
]

ignore_aaaa_domains = [
    "lync.com.",
    "nginx.org.",
    "timestamp.sectigo.com."
]

def operate(id, event, qstate, qdata):
    if event == MODULE_EVENT_NEW or event == MODULE_EVENT_PASS:

        if qstate.qinfo.qname_str.endswith(tuple(localhost_domains)):
            if (qstate.qinfo.qtype == RR_TYPE_AAAA):
                msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_AAAA, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
                msg.answer.append("%s 10 IN AAAA ::1" % qstate.qinfo.qname_str)
            if (qstate.qinfo.qtype == RR_TYPE_A):
                msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
                msg.answer.append("%s 10 IN A 127.0.0.1" % qstate.qinfo.qname_str)
            if (qstate.qinfo.qtype == RR_TYPE_ANY):
                msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_AAAA, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
                msg.answer.append("%s 10 IN AAAA ::1" % qstate.qinfo.qname_str)
                msg.answer.append("%s 10 IN A 127.0.0.1" % qstate.qinfo.qname_str)
            if not msg.set_return_msg(qstate):
                qstate.ext_state[id] = MODULE_ERROR
                return True
            # We don't need validation, result is valid
            qstate.return_msg.rep.security = 2
            qstate.return_rcode = RCODE_NOERROR
            qstate.ext_state[id] = MODULE_FINISHED
            log_info("mod.py: returned localhost for %s" % qstate.qinfo.qname_str)
            return True

        if qstate.qinfo.qname_str.endswith(tuple(ignore_aaaa_domains)):
            if (qstate.qinfo.qtype == RR_TYPE_AAAA):
                msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
                if not msg.set_return_msg(qstate):
                    qstate.ext_state[id] = MODULE_ERROR
                    return True
                # We don't need validation, result is valid
                qstate.return_msg.rep.security = 2
                qstate.return_rcode = RCODE_NOERROR
                qstate.ext_state[id] = MODULE_FINISHED
                log_info("mod.py: removed AAAA record from %s" % qstate.qinfo.qname_str)
                return True

        qstate.ext_state[id] = MODULE_WAIT_MODULE
        return True

    if event == MODULE_EVENT_MODDONE:
        qstate.ext_state[id] = MODULE_FINISHED
        return True

    log_err("mod.py: error in module occured")
    qstate.ext_state[id] = MODULE_ERROR
    return True

log_info("mod.py: script loaded")
