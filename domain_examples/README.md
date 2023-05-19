While built on propositional logic, will be defined using JSON (PDDL is predicate based and would be unnecessarily complex to parse and convert to propositional, but will be used if/when the project is converted to plan using predicate logic)

format:

```json
{
	"name":...,
	"operators":
	[
		{"name":..., "pre": {"p":"True", "q":"False", ...}, "eff": ["p":"False", ...]},
		...
	]
}
```
