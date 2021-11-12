from __future__ import absolute_import
from ...core import BaseClient
from requests import Session, Request
import six
import logging

logger = logging.getLogger(__name__)

class Client(BaseClient):
    """ Client implementation based on requests
    """

    __schemes__ = set(['http', 'https'])

    def __init__(self, auth=None, opt={}):
        """ constructor

        :param auth pyswagger.SwaggerAuth: auth info used when requesting
        :param send_opt dict: options used in requests.send, ex verify=False
        """
        super(Client, self).__init__(auth)

        self.__s = Session()
        self.__opt = opt

    def request(self, req_and_resp, opt={}, headers=None):
        """
        """

        # make sure all prepared state are clean before processing
        req, resp = req_and_resp
        req.reset()
        resp.reset()

        self.__opt.update(opt)

        req, resp = super(Client, self).request((req, resp), self.__opt)

        logger.info('client.opt: {0}'.format(str(self.__opt)))

        # apply request-related options before preparation
        scheme=self.prepare_schemes(req)
        if scheme:
            req.prepare(scheme=scheme, handle_files=False)
        else:
            req.prepare(handle_files=False)
        req._patch(self.__opt)

        composed_headers = self.compose_headers(req, headers, opt, as_dict=True)

        # prepare for uploaded files
        file_obj = []
        def append(name, obj):
            f = obj.data or open(obj.filename, 'rb')
            if 'Content-Type' in obj.header:
                file_obj.append((name, (obj.filename, f, obj.header['Content-Type'])))
            else:
                file_obj.append((name, (obj.filename, f)))

        for k, v in six.iteritems(req.files):
            if isinstance(v, list):
                for vv in v:
                    append(k, vv)
            else:
                append(k, v)

        rq = Request(
            method=req.method.upper(),
            url=req.url,
            params=req.query,
            data=req.data,
            headers=composed_headers,
            files=file_obj
        )
        rq = self.__s.prepare_request(rq)
        rs = self.__s.send(rq, stream=True, **self.__opt)

        resp.apply_with(
            status=rs.status_code,
            header=rs.headers,
            raw=six.BytesIO(rs.content).getvalue()
        )

        return resp
