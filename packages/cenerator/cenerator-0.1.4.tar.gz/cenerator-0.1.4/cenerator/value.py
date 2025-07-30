"""
Copyright (c) 2021-2025 Zakru

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from abc import ABC, abstractmethod


class NumberValue(ABC):
    """Reference to a number value"""

    @abstractmethod
    def to_storage(self, c, type: str) -> 'StorageValue':
        """Cast this number value reference to a storage reference"""
        ...

    @abstractmethod
    def to_json_text(self) -> str:
        """Converts this reference into a JSON text component"""
        ...

    @abstractmethod
    def to_snbt_text(self) -> str:
        """Converts this reference into an SNBT text component"""
        ...


class StorageValue(NumberValue):

    def __init__(self, storage: str, path: str, type: str):
        self.storage = storage
        self.path = path
        self.type = type
    
    def to_storage(self, c, type: str) -> 'StorageValue':
        if type == self.type:
            return self
        else:
            return c.store_storage(type, f'data get storage {self.storage} {self.path}')

    def to_json_text(self) -> str:
        return f'{{"storage":"{self.storage}","nbt":"{self.path}"}}'

    def to_snbt_text(self) -> str:
        return f'{{storage:"{self.storage}",nbt:"{self.path}"}}'
