# SpecialPointsConfig
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**String**](string.md) | Name of special point. | [default to null]
**nameMinussimple** | [**String**](string.md) | A table-friendly version of the name. | [optional] [default to null]
**description** | [**String**](string.md) | A table-friendly description of the point. | [optional] [default to null]
**ignore** | [**Boolean**](boolean.md) | Option to suppress plotting. | [optional] [default to false]
**ignoreMinus2D** | [**Boolean**](boolean.md) | Option to suppress plotting in 2D Plot. | [optional] [default to false]
**derivatives** | [**List**](integer.md) |  | [optional] [default to null]
**found** | [**Boolean**](boolean.md) | Option to mark whether point successfully computed. | [optional] [default to false]
**time** | [**BigDecimal**](number.md) | Time co-ordinate of special point (initially normalised to &#x60;[0, 1]&#x60;). | [optional] [default to -1]
**value** | [**BigDecimal**](number.md) | Value of special point. | [optional] [default to -1]
**spec** | [**SpecialPointsSpec**](SpecialPointsSpec.md) |  | [optional] [default to null]
**format** | [**PointFormat**](PointFormat.md) |  | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

