from __future__ import absolute_import
import uuid
import six

class SwaggerUUID(object):
    """ wrapper of uuid.UUID
    """
    def __init__(self):
        super(object, self).__init__()
        self.v = None

    def __str__(self):
        return str(self.v)

    def __repr__(self):
        return str(self.v)

    def to_json(self):
        return str(self.v)

    def apply_with(self, _, val, ctx):
        """ constructor

        :param val: things used to construct uuid
        :type val: uuid as byte, string, or uuid.UUID
        """
        if val == None:
            self.v = None
            return self.v
        if isinstance(val, uuid.UUID):
            self.v = val
        elif isinstance(val, six.string_types):
            try:
                self.v = uuid.UUID(val)
            except ValueError:
                self.v = uuid.UUID(bytes=val)
        elif isinstance(val, six.binary_type):
            # TODO: how to support bytes_le?
            self.v = uuid.UUID(bytes=val)
        else:
            raise ValueError('Unrecognized type for UUID: ' + str(type(val)))

        return self.v
