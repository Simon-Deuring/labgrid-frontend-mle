# Api Definition for WAMP RPC

## Places

- Request

  `place`

- Response

```json
{
   "places":
      [
         "place1", "place2", ...
      ]
}
```

## Resource

- Request

`resource(place_name)`

- Response

```json
{
   "resources": ["resource 1", "resource 2", ...]
}
```

- Request

`resource`

- Response
  - place-resource dict

```json
{
   "resources": [
      { "place1" : [ "resource 1", ...]}
      { "place2" : [ "resource 2", ...]},
      ...
      ]
}
```
## Resource as list with filter

### Resource by Name

- Request

   `resource_by_name`

   `resource_by_name(name)`

- Response

```json
[
   {
      "name" : "resource name",
      "target" : "resource target",
      "place" : "place of resource",
      ...
   },...
]

```

### Resource Overview

- Request

   `resource_overview`

   `resource_overview(place)`

- Response

```json
[
   {
      "name" : "resource name",
      "target" : "resource target",
      "place" : "place of resource",
      ...
   },...
]

```

## Power states

- Request

  `power_state(place_name)`

- Response

```json
{
   "place" : "place_name",
   "power_state" : "true"|"false"
}
```

## Errors

On errors RPC return an error object

```json
{
   "error" : {
      "kind" : ErrorKind,
      "message" : ErrorMessage
   }
}
```

### Error Kind

- InvalidParameter
- NotFound
