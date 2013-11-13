virtual full

@r1@
identifier fn;
expression ret, E;
@@
ret = fn(...);
... when != ret = E
IS_ERR(ret)

@x1 depends on !full forall@
identifier r1.fn;
type T;
@@
static T fn(...) {
  ...
}

@script:python depends on r1 && !x1 && !full@
fn << r1.fn;
@@
print "%s|IS_ERR" % fn

@script:python depends on r1 && full@
fn << r1.fn;
@@
print "%s|IS_ERR" % fn

@x2@
identifier fn, ret;
position p2;
@@
int ret;
...
ret = fn@p2(...);

@r2@
identifier fn != {ERR_PTR};
expression ret, E;
statement S;
position p != {x2.p2};
@@
ret = fn@p(...);
... when != ret = E
if (ret == NULL) S

@x3 depends on !full forall@
identifier r2.fn;
type T;
@@
static T fn(...) {
  ...
}

@script:python depends on r2 && !x3 && !full@
fn << r2.fn;
@@
print "%s|NULL" % fn

@script:python depends on r2 && full@
fn << r2.fn;
@@
print "%s|NULL" % fn

@r4@
identifier fn;
expression ret, E;
@@
ret = fn(...);
... when != ret = E
IS_ERR_OR_NULL(ret)

@x4 depends on !full forall@
identifier r4.fn;
type T;
@@
static T fn(...) {
  ...
}

@script:python depends on r4 && !x4 && !full@
fn << r4.fn;
@@
print "%s|IS_ERR_OR_NULL" % fn

@script:python depends on r4 && full@
fn << r4.fn;
@@
print "%s|IS_ERR_OR_NULL" % fn
