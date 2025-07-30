
#include <stdint.h>
#include <stdlib.h>
#include <math.h>

#define GRADIENT_SIZE 65536

float fade(float t) {
    return t * t * t * (t * (t * 6.f - 15.f) + 10.f);
}

float grad(float x) {
    static float gradients[GRADIENT_SIZE];
    static int initialized = 0;

    if (!initialized) {
        for (int i = 0; i < GRADIENT_SIZE; ++i) {
            gradients[i] = ((float)rand() / RAND_MAX) * 2.0f - 1.0f;
        }
        initialized = 1;
    }

    int idx = ((int)floorf(x)) % GRADIENT_SIZE;
    if (idx < 0) idx += GRADIENT_SIZE;
    return gradients[idx];
}

float perlin1d(float x) {
    float x0 = floorf(x);
    float x1 = x0 + 1.0f;
    float t = x - x0;
    float fade_t = fade(t);
    float g0 = grad(x0);
    float g1 = grad(x1);
    float d0 = (x - x0) * g0;
    float d1 = (x - x1) * g1;
    return (1.0f - fade_t) * d0 + fade_t * d1;
}

float fractal_perlin1d(float x, int octaves, float persistence, float lacunarity) {
    float total = 0.0f, amplitude = 1.0f, frequency = 1.0f, max_amp = 0.0f;
    for (int i = 0; i < octaves; ++i) {
        total += perlin1d(x * frequency) * amplitude;
        max_amp += amplitude;
        amplitude *= persistence;
        frequency *= lacunarity;
    }
    return total / max_amp;
}

// Fonction exportée : remplit un tableau de `count` échantillons
__attribute__((visibility("default")))
void generate_samples(float* out, int count, float base_freq, int octaves, float persistence, float lacunarity, int sample_rate) {
    for (int i = 0; i < count; ++i) {
        float t = (float)i / sample_rate;
        float x = t * base_freq;
        out[i] = fractal_perlin1d(x, octaves, persistence, lacunarity);
    }
}
