MACHINE StructTest3
CONSTANTS record
PROPERTIES
record : struct(a: STRING, b: POW(struct(c: INTEGER)))
& record = rec(a: "abc", b: {rec(c:1)})
END