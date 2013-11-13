@x1 forall@
position p1;
identifier fn;
type T;
@@
T fn@p1(...) {
<+...
return NULL;
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
E = NULL;
...
return E;
...+>
}

@r forall@
position p != {x1.p1, x2.p2};
identifier fn;
type T;
@@
T fn@p(...) {
<+...
return ERR_PTR(...);
...+>
}

@r2 forall@
position p != {x1.p1, x2.p2};
identifier fn;
expression E;
type T;
@@
T fn@p(...) {
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

@script:python depends on r@
fn << r.fn;
@@
print "%s" % fn

@script:python depends on r2@
fn << r2.fn;
@@
print "%s" % fn\n'