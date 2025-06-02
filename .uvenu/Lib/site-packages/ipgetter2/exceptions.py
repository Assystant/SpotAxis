# -*- coding: utf-8 -*-


class AddressNotFoundError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
