# InterpConfigPoly
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**special** | [**List**](string.md) | List of keys of special points whose conditions we will continue to force. | [optional] [default to []]
**points** | [**Map**](object.md) | A local environment of definitions in terms of period and special points. The expressions like \&quot;T\&quot; and \&quot;t[&#39;key&#39;]\&quot; and \&quot;x[&#39;key&#39;]\&quot; evaluate to period, time-coordiate and value of &#x60;&#39;key&#39;&#x60; respectively. | [optional] [default to {}]
**intervals** | [**List**](array.md) | Defines the spatial domain over which the model is to be defined. The remainder is an interpolation. | [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

