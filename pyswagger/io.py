from __future__ import absolute_import
from .utils import final, deref, CaseInsensitiveDict
from pyswagger import errs
from uuid import uuid4
import six
import io, codecs
import collections
import logging


logger = logging.getLogger(__name__)


class Request(object):
    """ Request layer
    """
    # TODO: make a new class for 'prepared' Request

    # option: url_netloc, replace netloc part in url, useful
    # when testing a set of Swagger APIs locally.
    opt_url_netloc = 'url_netloc'
    opt_url_scheme = 'url_scheme'

    def __init__(self, op, params):
        """ constrcutor

        :param Operation op: the related Operation object
        :param dict params: parameter set provided by user
        """

        self.__op = op
        self.__p = params
        self.__url = self.__op.url
        self.__path = self.__op.path
        self.__header = CaseInsensitiveDict()

        self.__consume = None
        self.__produce = None
        self.__scheme = None
        self.__data = []

    def reset(self):
        self.__url = self.__op.url
        self.__path = self.__op.path
        self.__header = CaseInsensitiveDict()
        self.__data = []

    def consume(self, consume):
        self.__consume = consume
        return self

    def produce(self, produce):
        self.__produce = produce
        return self

    def _prepare_forms(self, data):
        """ private function to prepare content for paramType=form
        """
        content_type = 'application/x-www-form-urlencoded'
        # Todo: OpenAPI uses requestBody/content[MediaType] instead of consumes
        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('content type {0} does not present in {1}'.format(content_type, self.__op.consumes))

        return content_type, six.moves.urllib.parse.urlencode(data)

    def _prepare_body(self, data, default_content_type='application/json'):
        """ private function to prepare content for paramType=body
        """
        content_type = self.__consume

        # Todo: OpenAPI uses requestBody/content[MediaType] instead of consumes
        if not content_type:
            content_type = self.__op.consumes[0] if self.__op.consumes else default_content_type

        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('content type {0} does not present in {1}'.format(content_type, self.__op.consumes))

        # according to SwaggerV2 spec, payload should be one and only,
        # so we just return the first value in dict.
        for parameter in self.__op.parameters:
            parameter = final(parameter)
            if getattr(parameter, 'in') == 'body':
                schema = deref(parameter.schema)
                _type = schema.type
                _format = schema.format
                name = schema.name
                body = data[parameter.name]
                return content_type, self.__op._mime_codec.marshal(content_type, body, _type=_type, _format=_format, name=name)

        return None,None

    def _prepare_mediatype(self, data, default_content_type='application/json'):
        content_type = self.__consume

        # Todo: OpenAPI uses requestBody/content[MediaType] instead of consumes
        if not content_type:
            content_type = self.__op.consumes[0] if self.__op.consumes else default_content_type

        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('content type {0} does not present in {1}'.format(content_type, self.__op.consumes))

        schema = self.__op.requestBody.content[content_type].schema
        schema = deref(schema)
        _type = schema.type
        _format = schema.format
        name = schema.name

        return content_type, self.__op._mime_codec.marshal(content_type, data, _type=_type, _format=_format, name=name)

    def _prepare_files(self, encoding, data):
        """ private function to prepare content for paramType=form with File
        """
        content_type = 'multipart/form-data'
        # Todo: OpenAPI uses requestBody/content[MediaType] instead of consumes
        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('content type {0} does not present in {1}'.format(content_type, self.__op.consumes))

        boundary = uuid4().hex
        content_type += '; boundary={0}'
        content_type = content_type.format(boundary)

        # init stream
        body = io.BytesIO()
        w = codecs.getwriter(encoding)

        def append(name, obj):
            body.write(six.b('--{0}\r\n'.format(boundary)))

            # header
            w(body).write('Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(name, obj.filename))
            body.write(six.b('\r\n'))
            if 'Content-Type' in obj.header:
                w(body).write('Content-Type: {0}'.format(obj.header['Content-Type']))
                body.write(six.b('\r\n'))
            if 'Content-Transfer-Encoding' in obj.header:
                w(body).write('Content-Transfer-Encoding: {0}'.format(obj.header['Content-Transfer-Encoding']))
                body.write(six.b('\r\n'))
            body.write(six.b('\r\n'))

            # body
            if not obj.data:
                with open(obj.filename, 'rb') as f:
                    body.write(f.read())
            else:
                filedata = obj.data.read()
                if isinstance(filedata, six.text_type):
                    w(body).write(filedata)
                else:
                    body.write(filedata)

            body.write(six.b('\r\n'))

        for k, v in self.__p['formData']:
            body.write(six.b('--{0}\r\n'.format(boundary)))

            w(body).write('Content-Disposition: form-data; name="{0}"'.format(k))
            body.write(six.b('\r\n'))
            body.write(six.b('\r\n'))

            w(body).write(v)

            body.write(six.b('\r\n'))

        # begin of file section
        for k, v in six.iteritems(data):
            if isinstance(v, list):
                for vv in v:
                    append(k, vv)
            else:
                append(k, v)

        # final boundary
        body.write(six.b('--{0}--\r\n'.format(boundary)))

        return content_type, body.getvalue()

    def _patch(self, opt={}):
        """ private function to patch this request. This function
        could be called before/after preparation.

        :param dict opt: options, used options would be popped. Refer to Request.opt_* for details.
        """
        opt_netloc = opt.pop(Request.opt_url_netloc, None)
        opt_scheme = opt.pop(Request.opt_url_scheme, None)

        if opt_netloc:
            self.__url = self.__url._replace(netloc=opt_netloc)
        if opt_scheme:
            self.__url = self.__url._replace(scheme=opt_scheme)

        logger.info('patching url: [{0}]'.format(str(self.__url)))

    def prepare(self, scheme=None, handle_files=True, encoding='utf-8'):
        """ make this request ready for Clients

        :param str scheme: scheme used in this request
        :param bool handle_files: False to skip multipart/form-data encoding
        :param str encoding: encoding for body content.
        :rtype: Request
        """
        if scheme != None:
            if isinstance(scheme, list):
                if self.__scheme is None:
                    scheme = scheme.pop()
                else:
                    if self.__scheme in scheme:
                        scheme = self.__scheme
                    else:
                        raise Exception('preferred scheme:{} is not supported by the client or spec:{}'.format(self.__scheme, scheme))
            elif not isinstance(scheme, six.string_types):
                raise ValueError('"scheme" should be a list or string')

            self.__url = self.__url._replace(scheme=scheme)

        # combine path parameters into path
        # TODO: 'dot' is allowed in swagger, but it won't work in python-format
        path_params = {}
        for k, v in self.__p['path']:
            path_params[k] = six.moves.urllib.parse.quote_plus(v)

        # combine path parameters into url
        try:
            self.__path = self.__path.format(**path_params)
            self.__url = self.__url._replace(path=self.__url.path.format(**path_params))
        except Exception as ex:
            raise ValueError("Could not encode url path {0} with path parameters {1}: Exception because of {2}".format(self.__url.path, str(path_params), str(ex)))

        # header parameters
        self.__header.update(self.__p['header'])

        # update data parameter
        content_type = None
        if self.__p['body']:
            content_type, data = self._prepare_body(self.__p['body'])
            self.__data.append((content_type,data))

        if self.__p['file']:
            if handle_files:
                content_type, data = self._prepare_files(encoding,self.__p['file'])
                self.__data.append((content_type,data))
            else:
                # client that can encode multipart/form-data, should
                # access form-data via data property and file from file
                # property.

                # only form data can be carried along with files,
                content_type = "multipart/form-data"
                self.__data.append((content_type, self.__p['formData']))

        if self.__p['formData']:
            content_type, data = self._prepare_forms(self.__p['formData'])
            self.__data.append((content_type,data))

        if self.__consume != None:
            if self.__consume in self.__p:
                content_type, data = self._prepare_mediatype(self.__p[self.__consume])
                self.__data.append((content_type,data))

        if self.__p['query']:
            query_params = []
            for name,val in self.__p['query']:
                query_params.append((name,str(val)))
            self.__p['query'] = query_params

        if content_type:
            self.__header.update({'Content-Type': content_type})

        accept = self.__produce
        if not accept and self.__op.produces:
            accept = self.__op.produces[0]
        if accept:
            if self.__op.produces and accept not in self.__op.produces:
                raise errs.SchemaError('accept {0} does not present in {1}'.format(accept, self.__op.produces))
            self.__header.update({'Accept': accept})

        return self

    @property
    def scheme(self):
        """ preferred scheme used in this request
        """
        return self.__scheme

    @scheme.setter
    def scheme(self, scheme):
        self.__scheme = scheme

    @property
    def url(self):
        """ url of this request, only valid after 'prepare'

        :type: str
        """
        fullurl = self.__url._replace(path=self.__url.path+self.__path)
        return fullurl.geturl()

    @property
    def path(self):
        """ path of this request, only valid after 'prepare'

        :type: str
        """
        return self.__path

    @property
    def base_path(self):
        """ base path of this request

        :type: str
        """
        return self.__op.base_path

    @property
    def query(self):
        """ query part of this request

        :type: dict
        """
        return self.__p['query']

    @property
    def method(self):
        """ HTTP verb of this request

        :type: str
        """
        return self.__op.method

    @property
    def header(self):
        """ header of this request, only valid after 'prepare'

        :type: pyswagger.util.CaseInsensitiveDict
        """
        return self.__header

    @property
    def data(self):
        """ data carried by this request, only valid after 'prepare'

        :type: byte
        """
        return self.__data

    @property
    def files(self):
        """ files of this Request

        :type: dict of (name, primitives.File)
        """
        return self.__p['file']

    @property
    def body(self):
        """ body of this Request

        :type: dict of (name, primitives)
        """
        return self.__p['body']


    @property
    def schemes(self):
        """ required schemes for current Operation.

        :type: list of str
        """
        return self.__op.cached_schemes

    @property
    def _p(self):
        """ access internal placeholder of all parameters,
        for unittest/debug/internal purpose
        """
        return self.__p

    @property
    def _security(self):
        """ list of authorizations required

        :type: dict of list of Authorizations object.
        """
        return self.__op.security


class Response(object):
    """ Response layer
    """

    def __init__(self, op):
        """ constructor

        :param Operation op: the related Operation object
        """
        self.__op = op
        self.__raw = self.__data = None

        # init properties
        self.__status = None
        self.__header = CaseInsensitiveDict()

        # options
        self.__raw_body_only = False

    def reset(self):
        self.__status = None
        self.__header = CaseInsensitiveDict()
        self.__raw = self.__data = None
        self.__path = self.__op.path
        self.__url = self.__op.url

    def _convert_header(self, resp, k, v):
        if resp and resp.headers and k in resp.headers:
            v = resp.headers[k]._prim_(v, self.__op._prim_factory, ctx=dict(read=True))

        if k in self.__header:
            self.__header[k].append(v)
        else:
            self.__header[k] = [v]

    def apply_with(self, status=None, raw=None, header=None):
        """ update header, status code, raw datum, ...etc

        :param int status: status code
        :param str raw: body content
        :param dict header: header section
        :return: return self for chaining
        :rtype: Response
        """

        if status != None:
            self.__status = status

        r = (final(self.__op.responses.get(str(self.__status), None)) or
             final(self.__op.responses.get('default', None)))

        if header != None:
            if isinstance(header, (collections.Mapping, collections.MutableMapping)):
                for k, v in six.iteritems(header):
                    self._convert_header(r, k, v)
            else:
                for k, v in header:
                    self._convert_header(r, k, v)

        if raw != None:
            # update 'raw'
            self.__raw = raw

            if self.__status == None:
                raise Exception('Update status code before assigning raw data')

            if r and r.schema and not self.__raw_body_only:
                # update data from Opeartion if succeed else from responseMessage.responseModel
                content_type = 'application/json'
                for k, v in six.iteritems(self.header):
                    if k.lower() == 'content-type':
                        content_type = v[0].lower()
                        break
                schema = deref(r.schema)
                _type = schema.type
                _format = schema.format
                name = schema.name
                data = self.__op._mime_codec.unmarshal(content_type, self.raw, _type=_type, _format=_format, name=name)
                self.__data = r.schema._prim_(data, self.__op._prim_factory, ctx=dict(read=True))

        return self

    def raw_body_only(self, only):
        """ an option to disable parsing bytes-stream to
        pyswagger primitives of body response. 'True' to enable this option
        """
        self.__raw_body_only = only

    raw_body_only = property(None, raw_body_only)

    @property
    def status(self):
        """ status code

        :type: int
        """
        return self.__status

    @property
    def data(self):
        """ responsed data

        :type: primitives.Model
        """
        return self.__data

    @property
    def raw(self):
        """ raw response

        :type: str
        """
        return self.__raw

    @property
    def header(self):
        """ header of Response

        :type: dict of list, ex. {'Content-Type': [xxx, xxx]}
        """
        return self.__header


SwaggerRequest = Request
SwaggerResponse = Response
