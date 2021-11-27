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
  - place-resource tuples

```json
{
   "resources": [
      { "place1" : [ "resource 1", ...]}
      { "place2" : [ "resource 2", ...]},
      ...
      ]
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
