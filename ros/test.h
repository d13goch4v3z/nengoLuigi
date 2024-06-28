#ifndef SINE_WAVE_ARRAY_GENERATOR_H
#define SINE_WAVE_ARRAY_GENERATOR_H

#include <vector>

class SineWaveArrayGenerator {
public:
    SineWaveArrayGenerator(int array_size, double scale, double shift);
    void generateSineWave();
    void printArray() const;

private:
    int array_size;
    double scale;
    double shift;
    std::vector<int> array;
};

#endif // SINE_WAVE_ARRAY_GENERATOR_H