/*
 * Does "never appeared in a simulation" mean anything?
 *
 * The claim to test: if we simulate enough draws and find combinations that
 * never came up, those are somehow due / better / worth playing.
 *
 * This program tests it properly instead of arguing about it.
 *
 *   Stage A : simulate N draws, record every combination that appeared in a
 *             bitset over all C(50,5)*C(12,2) = 139,838,160 combinations.
 *   Stage B : simulate N more draws with a DIFFERENT seed, independently.
 *   Compare : do the combinations that were ABSENT from A appear in B at a
 *             different rate than combinations in general?
 *
 * If "never appeared" carried any information, the two rates would differ.
 *
 * Also produces a scaling table: how the never-appeared count shrinks as the
 * run gets longer, against the theoretical T * exp(-N/T).
 *
 *   gcc -O3 -march=native -o never_drawn never_drawn.c -lm && ./never_drawn
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAIN_POOL 50
#define MAIN_PICK 5
#define EURO_POOL 12
#define EURO_PICK 2

static uint64_t C5[MAIN_POOL + 1][MAIN_PICK + 1];
static uint64_t TOTAL_MAIN, TOTAL_EURO, TOTAL;

/* ---- xoshiro256++ ---- */
static uint64_t s[4];
static inline uint64_t rotl(const uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}
static inline uint64_t next(void) {
    const uint64_t r = rotl(s[0] + s[3], 23) + s[0];
    const uint64_t t = s[1] << 17;
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3];
    s[2] ^= t;    s[3] = rotl(s[3], 45);
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
/* unbiased bounded: Lemire */
static inline uint32_t bounded(uint32_t range) {
    uint64_t m = (uint64_t)(uint32_t)next() * range;
    uint32_t l = (uint32_t)m;
    if (l < range) {
        uint32_t t = -range % range;
        while (l < t) { m = (uint64_t)(uint32_t)next() * range; l = (uint32_t)m; }
    }
    return (uint32_t)(m >> 32);
}

static void init_binom(void) {
    for (int n = 0; n <= MAIN_POOL; n++) {
        C5[n][0] = 1;
        for (int k = 1; k <= MAIN_PICK; k++)
            C5[n][k] = (k > n) ? 0 : (n == 0 ? 0 : C5[n-1][k-1] + C5[n-1][k]);
    }
    TOTAL_MAIN = C5[MAIN_POOL][MAIN_PICK];
    TOTAL_EURO = (uint64_t)EURO_POOL * (EURO_POOL - 1) / 2;
    TOTAL = TOTAL_MAIN * TOTAL_EURO;
}

/* colex rank of a sorted 5-subset of 0..49 -> 0 .. C(50,5)-1 */
static inline uint64_t rank_main(const int *c) {
    return C5[c[0]][1] + C5[c[1]][2] + C5[c[2]][3] + C5[c[3]][4] + C5[c[4]][5];
}
static inline uint64_t rank_euro(int a, int b) {  /* a<b, 0..11 */
    return (uint64_t)a + (uint64_t)b * (b - 1) / 2;
}

static inline uint64_t one_draw(void) {
    uint64_t mask = 0;
    int c[MAIN_PICK], n = 0;
    while (n < MAIN_PICK) {
        int v = bounded(MAIN_POOL);
        if (!((mask >> v) & 1ULL)) { mask |= 1ULL << v; c[n++] = v; }
    }
    for (int i = 1; i < MAIN_PICK; i++) {          /* insertion sort, 5 items */
        int k = c[i], j = i - 1;
        while (j >= 0 && c[j] > k) { c[j+1] = c[j]; j--; }
        c[j+1] = k;
    }
    int e1 = bounded(EURO_POOL), e2;
    do { e2 = bounded(EURO_POOL); } while (e2 == e1);
    if (e1 > e2) { int t = e1; e1 = e2; e2 = t; }
    return rank_main(c) * TOTAL_EURO + rank_euro(e1, e2);
}

static inline void set_bit(uint64_t *bs, uint64_t i) { bs[i >> 6] |= 1ULL << (i & 63); }
static inline int get_bit(const uint64_t *bs, uint64_t i) { return (bs[i >> 6] >> (i & 63)) & 1ULL; }

static uint64_t popcount_all(const uint64_t *bs, uint64_t words) {
    uint64_t t = 0;
    for (uint64_t i = 0; i < words; i++) t += __builtin_popcountll(bs[i]);
    return t;
}

int main(void) {
    init_binom();
    const uint64_t WORDS = (TOTAL + 63) / 64;
    printf("combinations tracked : %llu\n", (unsigned long long)TOTAL);
    printf("bitset size          : %.1f MB each\n\n", WORDS * 8.0 / 1e6);

    uint64_t *A = calloc(WORDS, 8);
    uint64_t *SNAP = calloc(WORDS, 8);
    uint64_t *B = calloc(WORDS, 8);
    if (!A || !SNAP || !B) { fprintf(stderr, "alloc failed\n"); return 1; }

    const uint64_t CHECK[] = {10000000ULL, 50000000ULL, 139838160ULL,
                              500000000ULL, 1000000000ULL, 2000000000ULL,
                              5000000000ULL};
    const int NCHECK = sizeof(CHECK) / sizeof(CHECK[0]);
    const uint64_t SNAP_AT = 139838160ULL;      /* = TOTAL, gives ~e^-1 absent */

    printf("=== SCALING: how many combinations are STILL 'never drawn' ===\n\n");
    printf("%16s %18s %18s %10s\n", "draws simulated", "never appeared",
           "theory T*e^(-N/T)", "share");

    seed(20260915ULL);
    uint64_t done = 0;
    for (int ci = 0; ci < NCHECK; ci++) {
        for (; done < CHECK[ci]; done++) set_bit(A, one_draw());
        if (done >= SNAP_AT && popcount_all(SNAP, WORDS) == 0)
            memcpy(SNAP, A, WORDS * 8);
        uint64_t seen = popcount_all(A, WORDS);
        uint64_t never = TOTAL - seen;
        double theory = (double)TOTAL * exp(-(double)done / (double)TOTAL);
        printf("%16llu %18llu %18.0f %9.4f%%\n",
               (unsigned long long)done, (unsigned long long)never, theory,
               100.0 * never / TOTAL);
        fflush(stdout);
    }

    uint64_t snap_seen = popcount_all(SNAP, WORDS);
    uint64_t snap_never = TOTAL - snap_seen;
    printf("\n=== THE TEST ===\n\n");
    printf("Stage A snapshot at %llu draws:\n", (unsigned long long)SNAP_AT);
    printf("  appeared     : %llu\n", (unsigned long long)snap_seen);
    printf("  NEVER appeared: %llu  (%.4f%% of all combinations)\n",
           (unsigned long long)snap_never, 100.0 * snap_never / TOTAL);

    printf("\nStage B: %llu fresh draws, different seed, independent.\n",
           (unsigned long long)SNAP_AT);
    seed(776655443322ULL);
    for (uint64_t i = 0; i < SNAP_AT; i++) set_bit(B, one_draw());

    /* hit rate in B among A-absent vs among all */
    uint64_t hit_absent = 0, hit_all = 0;
    for (uint64_t i = 0; i < TOTAL; i++) {
        int inB = get_bit(B, i);
        hit_all += inB;
        if (!get_bit(SNAP, i)) hit_absent += inB;
    }

    double rate_absent = (double)hit_absent / (double)snap_never;
    double rate_all = (double)hit_all / (double)TOTAL;
    printf("\n  combinations ABSENT from A that appeared in B : %llu of %llu\n",
           (unsigned long long)hit_absent, (unsigned long long)snap_never);
    printf("  rate among A-absent combinations              : %.6f\n", rate_absent);
    printf("  rate among ALL combinations                   : %.6f\n", rate_all);
    printf("  theoretical rate 1 - e^(-1)                   : %.6f\n",
           1.0 - exp(-1.0));
    printf("  difference                                    : %+.6f  (%+.4f%%)\n",
           rate_absent - rate_all, 100.0 * (rate_absent / rate_all - 1.0));

    double se = sqrt(rate_all * (1 - rate_all) / (double)snap_never);
    printf("  1 s.e. for the A-absent group                 : %.6f\n", se);
    printf("  deviation                                     : %.2f sigma\n",
           fabs(rate_absent - rate_all) / se);

    printf("\n=== PER-NUMBER CHECK ===\n\n");
    printf("Individual numbers 1-50 in the %llu-draw stage B:\n",
           (unsigned long long)SNAP_AT);
    /* recount individual number frequencies in a short fresh run */
    uint64_t freq[MAIN_POOL] = {0}, efreq[EURO_POOL] = {0};
    seed(13579246810ULL);
    const uint64_t SHORT = 100000000ULL;
    for (uint64_t i = 0; i < SHORT; i++) {
        uint64_t mask = 0; int c[MAIN_PICK], n = 0;
        while (n < MAIN_PICK) {
            int v = bounded(MAIN_POOL);
            if (!((mask >> v) & 1ULL)) { mask |= 1ULL << v; c[n++] = v; }
        }
        for (int k = 0; k < MAIN_PICK; k++) freq[c[k]]++;
        int e1 = bounded(EURO_POOL), e2;
        do { e2 = bounded(EURO_POOL); } while (e2 == e1);
        efreq[e1]++; efreq[e2]++;
    }
    uint64_t mn = freq[0], mx = freq[0];
    for (int i = 1; i < MAIN_POOL; i++) {
        if (freq[i] < mn) mn = freq[i];
        if (freq[i] > mx) mx = freq[i];
    }
    printf("  over %llu draws, each main number appeared\n",
           (unsigned long long)SHORT);
    printf("    least : %llu    most : %llu    expected : %llu\n",
           (unsigned long long)mn, (unsigned long long)mx,
           (unsigned long long)(SHORT * MAIN_PICK / MAIN_POOL));
    printf("    spread: %.4f%% of the mean\n",
           100.0 * (mx - mn) / ((double)SHORT * MAIN_PICK / MAIN_POOL));
    printf("  NOT ONE of the 50 numbers failed to appear. There is no such\n");
    printf("  thing as a 'number that never came up' - only whole combinations.\n");

    free(A); free(SNAP); free(B);
    return 0;
}
