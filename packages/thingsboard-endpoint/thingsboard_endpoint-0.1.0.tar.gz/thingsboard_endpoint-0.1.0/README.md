# ThingsBoard Endpoint

> Note: 
> 
> This is not an official project of the [ThingsBoard](https://thingsboard.io/) authors! Please refer to 
> [ThingsBoard - Open-source IoT Platform](https://github.com/thingsboard) for official ThingsBoard projects!

The ThingsBoard Endpoint package adds a data Meta-Model to the ThingsBoard devices sending data over MQTT. This 
allows to provide a data model for each device type.

The devices providing telemetry and attributes information to ThingsBoard are named **Endpoint**s to remove confusion 
added when using names like _clients_ or _devices_. 

## Endpoint Data Meta-Model
The object meta-structure is given as follows: 
 - An EndPoint can have Nodes
 - Nodes can have Objects
 - Objects can have Objects and/or Attributes

The [Attribute](https://gitlab.com/things-board/thingsboard-endpoint/-/blob/main/src/thingsboard/endpoint/attribute/attribute.py) objects represent the leafs in the data structure. 

An `Attribute` is responsible to synchronise a variable or an attribute to the cloud. Depending on the write policy the
attribute may be changed from the cloud in which case the attribute gets updated on the endpoint.

To set up your endpoint data model you should first think about how you would like to show up your IoT device in the 
cloud, keeping in mind the _EndPoint->Node->Object->Attribute_ meta-structure implied.

We encourage you to provide the data model using an [XML](https://en.wikipedia.org/wiki/XML) or 
[JSON](https://en.wikipedia.org/wiki/JSON) based file. The file needs then to be parsed and the Endpoint's object 
structure set up accordingly. There are [Factory](https://gitlab.com/things-board/thingsboard-endpoint/-/tree/main/src/thingsboard/endpoint/factory)
classes provided to simplify this process (XML only for the moment). The `Factory` class reads a data model file and 
creates the Endpoint object.
