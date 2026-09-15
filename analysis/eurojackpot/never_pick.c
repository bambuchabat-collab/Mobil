/*
 * Takes the request literally: simulate, then actually PICK combinations that
 * never came up, and print them as real numbers so they can be priced.
 *
 *   gcc -O3 -march=native -o never_pick never_pick.c && ./never_pick
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define MP 50
#define MK 5
#define EP 12

static uint64_t C5[MP + 1][MK + 1];
static uint64_t TM, TE, TOTAL;

static uint64_t s[4];
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t next(void) {
    const uint64_t r = rotl(s[0] + s[3], 23) + s[0];
    const uint64_t t = s[1] << 17;
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3];
    s[2] ^= t; s[3] = rotl(s[3], 45);
    return r;
}
static void seed(uint64_t x) {
    for (int i = 0; i < 4; i++) {
        x += 0x9E3779B97F4A7C15ULL;
        uint64_t z = x;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        s[i] = z ^ (z >> 31);
    }
    for (int i = 0; i < 20; i++) next();
}
static inline uint32_t bounded(uint32_t r) {
    uint64_t m = (uint64_t)(uint32_t)next() * r;
    uint32_t l = (uint32_t)m;
    if (l < r) { uint32_t t = -r % r; while (l < t) { m = (uint64_t)(uint32_t)next() * r; l = (uint32_t)m; } }
    return (uint32_t)(m >> 32);
}
static void init(void) {
    for (int n = 0; n <= MP; n++) {
        C5[n][0] = 1;
        for (int k = 1; k <= MK; k++)
            C5[n][k] = (k > n) ? 0 : (n == 0 ? 0 : C5[n-1][k-1] + C5[n-1][k]);
    }
    TM = C5[MP][MK]; TE = EP * (EP - 1) / 2; TOTAL = TM * TE;
}
static inline uint64_t rank_main(const int *c) {
    return C5[c[0]][1] + C5[c[1]][2] + C5[c[2]][3] + C5[c[3]][4] + C5[c[4]][5];
}
/* inverse of the colex rank: index -> sorted 5-subset of 0..49 */
static void unrank_main(uint64_t r, int *out) {
    for (int k = MK; k >= 1; k--) {
        int v = k - 1;
        while (C5[v + 1][k] <= r) v++;
        out[k - 1] = v;
        r -= C5[v][k];
    }
}
static void unrank_euro(uint64_t r, int *a, int *b) {
    int y = 1;
    while ((uint64_t)(y + 1) * y / 2 <= r) y++;
    *b = y; *a = (int)(r - (uint64_t)y * (y - 1) / 2);
}
static inline void setb(uint64_t *bs, uint64_t i) { bs[i >> 6] |= 1ULL << (i & 63); }
static inline int getb(const uint64_t *bs, uint64_t i) { return (bs[i >> 6] >> (i & 63)) & 1ULL; }

int main(void) {
    init();
    uint64_t W = (TOTAL + 63) / 64;
    uint64_t *A = calloc(W, 8);
    const uint64_t N = 139838160ULL;

    seed(424242ULL);
    for (uint64_t i = 0; i < N; i++) {
        uint64_t mask = 0; int c[MK], n = 0;
        while (n < MK) { int v = bounded(MP); if (!((mask >> v) & 1ULL)) { mask |= 1ULL << v; c[n++] = v; } }
        for (int i2 = 1; i2 < MK; i2++) { int k = c[i2], j = i2 - 1; while (j >= 0 && c[j] > k) { c[j+1] = c[j]; j--; } c[j+1] = k; }
        int e1 = bounded(EP), e2; do { e2 = bounded(EP); } while (e2 == e1);
        if (e1 > e2) { int t = e1; e1 = e2; e2 = t; }
        setb(A, rank_main(c) * TE + ((uint64_t)e1 + (uint64_t)e2 * (e2 - 1) / 2));
    }

    printf("Simulated %llu draws. Combinations that NEVER came up:\n\n",
           (unsigned long long)N);

    /* print the first few never-seen combinations */
    int shown = 0;
    for (uint64_t i = 0; i < TOTAL && shown < 6; i++) {
        if (getb(A, i)) continue;
        int m[MK], a, b;
        unrank_main(i / TE, m);
        unrank_euro(i % TE, &a, &b);
        printf("  #%d  main %2d %2d %2d %2d %2d   euro %2d %2d\n", shown + 1,
               m[0]+1, m[1]+1, m[2]+1, m[3]+1, m[4]+1, a+1, b+1);
        shown++;
    }

    /* did the two recommended tickets come up in this run? */
    int t1[MK] = {34, 35, 39, 44, 48};       /* 35 36 40 45 49, zero-based */
    int t2[MK] = {31, 37, 42, 43, 46};       /* 32 38 43 44 47 */
    uint64_t i1 = rank_main(t1) * TE + (6 + (uint64_t)10 * 9 / 2);   /* euro 7,11 */
    uint64_t i2 = rank_main(t2) * TE + (4 + (uint64_t)11 * 10 / 2);  /* euro 5,12 */
    printf("\nOur two recommended combinations in this same run:\n");
    printf("  35 36 40 45 49 + 7 11 : %s\n", getb(A, i1) ? "appeared" : "NEVER appeared");
    printf("  32 38 43 44 47 + 5 12 : %s\n", getb(A, i2) ? "appeared" : "NEVER appeared");
    printf("\nWhichever way those landed, it was decided by the seed of a\n");
    printf("pseudo-random generator on this machine - not by anything in\n");
    printf("Helsinki. Re-seed and the answer flips.\n");

    free(A);
    return 0;
}
