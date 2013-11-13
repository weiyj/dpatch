@x1 forall@
position p1;
identifier fn;
type T;
@@
T fn@p1(...) {
<+...
return ERR_PTR(...);
...+>
}

@x2 forall@
position p2;
identifier fn;
expression E;
type T;
@@
T fn@p2(...) {
<+...
(
E = ERR_PTR(...);
...
return E;
|
if (IS_ERR(E)) return E;
)
...+>
}

@x3 forall@
position p3;
identifier fn;
type T;
@@
static T fn@p3(...) {
  ...
}

@r1 forall@
position p != {x1.p1, x2.p2, x3.p3};
identifier fn;
type T;
@@
T fn@p(...) {
<+...
return NULL;
...+>
}

@r2 forall@
position p != {x1.p1, x2.p2, x3.p3};
identifier fn;
expression E, E2 != {NULL};
type T;
@@
T fn@p(...) {
<+...
E = NULL;
... when != E = E2
return E;
...+>
}

@script:python depends on r1@
fn << r1.fn;
@@
print "%s" % fn

@script:python depends on r2@
fn << r2.fn;
@@
print "%s" % fn