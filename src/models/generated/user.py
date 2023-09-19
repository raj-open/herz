# generated by datamodel-codegen:
#   filename:  schema-user.yaml

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Extra, Field


class Font(BaseModel):
    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    family: str = 'Tahoma'
    size: int = Field(12, description='Size of font (in entire plot) in `pt`.')
    size_title: int = Field(12, alias='size-title', description='Size of title font in `pt`.')


class PathToDirString(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(
        ...,
        description='Data type for a string to be a path to a directory.',
        regex='^[^\\\\\\/]+([\\\\\\/][^\\\\\\/]+)*$',
    )


class FileString(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(
        ...,
        description='Data type for a string to be the base name of a file.',
        regex='^[^\\\\\\/]*\\.[^\\\\\\/]+$',
    )


class PathToFileString(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(
        ...,
        description='Data type for a string to be a path to a file.',
        regex='^[^\\\\\\/]+([\\\\\\/][^\\\\\\/]+)*\\.[^\\\\\\/]+$',
    )


class PythonImportString(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(
        ...,
        description="Data type for a string to constitute an import 'path' in python.",
        regex='^(\\.\\.|\\.)[\\w\\_]+(\\.[\\w\\_]+)*$',
    )


class EnumType(str, Enum):
    """
    Enumeration of settings for log level.
    """

    BOOLEAN = 'bool'
    DOUBLE = 'float'
    INTEGER = 'int'
    STRING = 'str'


class DataTimeSeriesCommon(BaseModel):
    """
    Parameter options for combining time series.
    """

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

    dt: float = Field(..., gt=0.0)
    t_max: Optional[float] = Field(None, alias='T-max', gt=0.0)
    unit: str


class DataTypeQuantity(BaseModel):
    """
    Structure for physical quantity as column
    """

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    name: Any = Field(..., description='Name of column in file.')
    type: EnumType = Field(EnumType.DOUBLE, description='Data type (float, int, etc.)')
    unit: str = Field(..., description='Physical unit as string')


class EnumLogLevel(str, Enum):
    """
    Enumeration of settings for log level.
    """

    INFO = 'INFO'
    DEBUG = 'DEBUG'


class UserBasicOptions(BaseModel):
    """
    Basic options for running the programme.
    """

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    log_level: EnumLogLevel = Field(..., alias='log-level')
    verbose: bool = False


class Quantities(BaseModel):
    class Config:
        allow_population_by_field_name = True

    time: DataTypeQuantity
    pressure: DataTypeQuantity
    volume: DataTypeQuantity


class Table(BaseModel):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

    path: Optional[PathToDirString] = None
    sep: str
    decimal: str


class Plot(BaseModel):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

    path: Optional[PathToDirString] = None
    title: str
    legend: bool = False
    font: Font


class UserOutput(BaseModel):
    """
    Options for outputs
    """

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

    name: str = Field(..., description='Name of case.')
    quantities: Quantities
    table: Table
    plot: Plot


class DataTimeSeries(BaseModel):
    """
    Structure for time series.
    """

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    path: PathToDirString = Field(..., description='Path to file containing time series.')
    sep: str = Field(';', description='Delimiter for columns used in file.')
    decimal: str = Field('.', description='Symbol for decimals used in file.')
    skip: Union[int, List[int], str] = Field(
        [],
        description='Which row indexes to skip.\nEither provide\n\n- a string of a lambda function (mapping integers to boolean values)\n- an integer, indicating how many rows to skip from the top\n- an array\n\nNoted that row numbers are **0-based**!',
        examples={
            'simple': {'value': 3, 'summary': 'Rows `0,1,2` will be skipped.'},
            'function': {
                'value': '`lambda i: i % 3 == 1`',
                'summary': 'Skips every 3rd rwo starting from row-index 1',
            },
            'array': {
                'value': [0, 1, 2, 4, 5],
                'summary': 'In this case in the file\n- extra headers are on lines `0, 1, 2``,\n- headers are on row `3`\n- rows 4 and 5 contain further skippable content\n\nNOTE: negative values will be ignored.',
            },
        },
    )
    time: DataTypeQuantity = Field(..., description='Column name for time.')
    value: DataTypeQuantity = Field(..., description='Column name for value.')


class UserData(BaseModel):
    """
    Options for structure of data files.
    """

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    combine: DataTimeSeriesCommon
    pressure: DataTimeSeries
    volume: DataTimeSeries


class UserConfig(BaseModel):
    """
    Data model for all parts of the user configuration.
    """

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    basic: UserBasicOptions
    data: UserData
    output: Optional[UserOutput] = None