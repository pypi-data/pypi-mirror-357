#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned char u8;

// Linear allocator
typedef struct
{
  void *data;
  int limit;
  int used;
} lalloc;

#define lalloc_assert(l)   \
  assert ((l)->data);      \
  assert ((l)->limit > 0); \
  assert ((l)->used <= (l)->limit)

static void *
lmalloc (lalloc *a, u32 req, u32 size)
{
  lalloc_assert (a);
  assert (req > 0);
  assert (size > 0);

  u32 total = req * size;
  u32 avail = a->limit - a->used;
  if (avail < total)
    return NULL;

  u8 *base = (u8 *)a->data;
  void *ret = base + a->used;
  a->used += total;
  return ret;
}

static u8 heap[90000];
static lalloc galloc = { .data = heap, .limit = 90000, .used = 0 };

// Dynamic alloc happens on one big chunk
static void *
i_malloc (u32 req, u32 size)
{
  return lmalloc (&galloc, req, size);
}
static void *
i_calloc (u32 req, u32 size)
{
  void *ret = lmalloc (&galloc, req, size);
  if (ret)
    memset (ret, 0, req * size);
  return ret;
}

// Intrusive red black tree data structure
typedef struct tree_s tree;
struct tree_s
{
  tree *parent;
  tree *left;
  tree *right;
};

#define container_of(ptr, type, member) \
  ((type *)((char *)(ptr) - offsetof (type, member)))

// Allocate the first tree
static tree *
tree_create (void)
{
  return i_calloc (1, sizeof (tree));
}

// Find where [n] belongs
static tree **
tree_search_slot (
    tree **root,
    tree *n,
    int (*cmp) (const tree *, const tree *),
    tree **parent_out)
{
  tree **link = root, *parent = NULL;

  while (*link)
    {
      parent = *link;
      int c = cmp (n, parent);
      if (c < 0)
        {
          link = &parent->left;
        }
      else if (c > 0)
        {
          link = &parent->right;
        }
      else
        {
          return NULL;
        }
    }
  if (parent_out)
    {
      *parent_out = parent;
    }
  return link;
}

static int
tree_insert (
    tree **root,
    tree *n,
    int (*cmp) (const tree *, const tree *))
{
  tree *parent;
  tree **slot = tree_search_slot (root, n, cmp, &parent);

  if (!slot)
    {
      return -1;
    }

  n->left = n->right = NULL;
  n->parent = parent;
  *slot = n;

  return 0;
}

static tree *
tree_min (tree *n)
{
  while (n && n->left)
    {
      n = n->left;
    }
  return n;
}

typedef struct
{
  tree base;
  int lo, hi;
  int max;
} range_node;

static range_node *
range_node_create (int lo, int hi)
{
  range_node *n = i_malloc (1, sizeof (*n));
  if (!n)
    {
      return NULL;
    }
  n->base.parent = n->base.left = n->base.right = NULL;
  n->lo = lo;
  n->hi = hi;
  n->max = hi;
  return n;
}

static int
range_cmp (const tree *a, const tree *b)
{
  const range_node *ra = container_of (a, range_node, base);
  const range_node *rb = container_of (b, range_node, base);
  if (ra->lo < rb->lo)
    {
      return -1;
    }
  if (ra->lo > rb->lo)
    {
      return 1;
    }
  if (ra->hi < rb->hi)
    {
      return -1;
    }
  if (ra->hi > rb->hi)
    {
      return 1;
    }
  return 0;
}

static void
range_update_max (range_node *n)
{
  int max_hi = n->hi;

  if (n->base.left)
    {
      range_node *l = container_of (n->base.left, range_node, base);
      if (l->max > max_hi)
        {
          max_hi = l->max;
        }
    }
  if (n->base.right)
    {
      range_node *r = container_of (n->base.right, range_node, base);
      if (r->max > max_hi)
        {
          max_hi = r->max;
        }
    }
  n->max = max_hi;
}

static void
range_fixup_ancestors (range_node *n)
{
  while (n)
    {
      int old = n->max;
      range_update_max (n);
      if (n->max == old)
        {
          break;
        }
      n = n->base.parent ? container_of (n->base.parent, range_node, base) : NULL;
    }
}

/* public insert */
static int
range_tree_insert (range_node **root, range_node *n)
{
  n->max = n->hi; /* initialise */
  int rc = tree_insert ((tree **)root, &n->base, range_cmp);
  if (rc == 0)
    {
      range_fixup_ancestors (n);
    }
  return rc;
}

/* interval overlap test */
static inline int
ranges_overlap (int lo1, int hi1, int lo2, int hi2)
{
  return lo1 <= hi2 && lo2 <= hi1;
}

/* find one node that overlaps [lo,hi] */
static range_node *
range_tree_find_overlap (range_node *root, int lo, int hi)
{
  range_node *cur = root;
  while (cur)
    {
      if (ranges_overlap (cur->lo, cur->hi, lo, hi))
        return cur;

      if (cur->base.left)
        {
          range_node *l = container_of (cur->base.left, range_node, base);
          if (l->max >= lo)
            {
              cur = l;
              continue;
            }
        }
      cur = cur->base.right ? container_of (cur->base.right, range_node, base)
                            : NULL;
    }
  return NULL;
}

int
main (void)
{
  range_node *root = NULL;
  int ranges[][2] = { { 5, 7 }, { 1, 2 }, { 6, 10 }, { 12, 13 }, { 3, 4 } };

  for (int i = 0; i < 5; i++)
    {
      range_node *n = range_node_create (ranges[i][0], ranges[i][1]);
      assert (range_tree_insert (&root, n) == 0);
    }

  int qlo = 6, qhi = 6;
  range_node *hit = range_tree_find_overlap (root, qlo, qhi);
  if (hit)
    {
      printf ("found [%d,%d] overlaps [%d,%d]\n", hit->lo, hit->hi, qlo, qhi);
    }
  else
    {
      printf ("no overlap for [%d,%d]\n", qlo, qhi);
    }

  return 0;
}
