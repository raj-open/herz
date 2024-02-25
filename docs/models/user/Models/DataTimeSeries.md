# DataTimeSeries
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**path** | [**String**](string.md) | Data type for a string to be a path to a directory. | [default to null]
**sep** | [**String**](string.md) | Delimiter for columns used in file. | [optional] [default to ;]
**decimal** | [**String**](string.md) | Symbol for decimals used in file. | [optional] [default to .]
**skip** | [**oneOf&lt;integer,array,string&gt;**](oneOf&lt;integer,array,string&gt;.md) | Which row indexes to skip. Either provide  - a string of a lambda function (mapping integers to boolean values) - an integer, indicating how many rows to skip from the top - an array  Noted that row numbers are **0-based**! | [optional] [default to null]
**time** | [**DataTypeQuantity**](DataTypeQuantity.md) |  | [default to null]
**value** | [**DataTypeQuantity**](DataTypeQuantity.md) |  | [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

