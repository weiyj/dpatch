@e@
type T;
expression c;
identifier x;
@@
(
T x;
...
 x = \(kmem_cache_alloc\|kmem_cache_zalloc\|kmem_cache_alloc_node\)(c,...);
|
T x= \(kmem_cache_alloc\|kmem_cache_zalloc\|kmem_cache_alloc_node\)(c,...);
)

@script:python depends on e@
T << e.T;
c << e.c;
@@

print "%s|%s" % (T, c)