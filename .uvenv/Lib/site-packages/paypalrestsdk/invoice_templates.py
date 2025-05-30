import paypalrestsdk.util as util
from paypalrestsdk.resource import List, Find, Delete, Create, Update, Post, Resource
from paypalrestsdk.api import default as default_api

class InvoiceTemplate(List, Find, Create, Delete, Update):
    """InvoiceTemplate class wrapping the REST v1/invoicing/templates endpoint"

    Usage::
        >>> templates = InvoiceTemplate.all()

        >>> invoice_template = InvoiceTemplate.new({})
        >>> invoice.create() # return True or False
    """
    path = "v1/invoicing/templates"

    def __getitem__(self, key):
        if key == 'id':
            return self.__data__['template_id']
        else:
            return super.__getitem__(self, key)

