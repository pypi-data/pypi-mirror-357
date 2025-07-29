#pragma once

#include <complex>
#include <cstdint>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <type_traits>
#include <typeindex>
#include <unordered_map>
#include <vector>

#include <urx/detail/compare.h>  // IWYU pragma: keep
#include <urx/enums.h>

namespace urx {

template <typename T>
struct IsComplex : public std::false_type {};

template <typename T>
struct IsComplex<std::complex<T>> : public std::true_type {};

template <typename T>
struct IsComplex<std::vector<std::complex<T>>> : public std::true_type {};

template <typename T>
constexpr bool is_complex() {
  return IsComplex<T>::value;
}

template <typename T>
constexpr bool is_complex(const T&) {
  return is_complex<T>();
}

class RawData {
 public:
  virtual const void* getBuffer() const = 0;
  virtual void* getBuffer() = 0;
  virtual size_t getSize() const = 0;
  virtual SamplingType getSamplingType() const = 0;
  virtual DataType getDataType() const = 0;

  bool operator==(const RawData& other) const {
    // Also exist in urx::utils::group_helper::sizeofDataType.
    static std::unordered_map<DataType, size_t> group_dt_to_sizeof{
        {DataType::INT16, sizeof(int16_t)},
        {DataType::INT32, sizeof(int32_t)},
        {DataType::FLOAT, sizeof(float)},
        {DataType::DOUBLE, sizeof(double)}};
    return getSamplingType() == other.getSamplingType() && getDataType() == other.getDataType() &&
           getSize() == other.getSize() &&
           std::memcmp(getBuffer(), other.getBuffer(),
                       getSize() * group_dt_to_sizeof.at(getDataType()) *
                           (getSamplingType() == SamplingType::RF ? 1 : 2)) == 0;
  }

  virtual ~RawData() = default;
};

template <typename T>
class IRawData : public RawData {
 public:
  using ValueType = T;

  SamplingType getSamplingType() const override {
    return IsComplex<ValueType>::value ? SamplingType::IQ : SamplingType::RF;
  };

  DataType getDataType() const override {
    const std::type_index type([]() -> std::type_index {
      if constexpr (IsComplex<ValueType>::value) {
        return typeid(typename ValueType::value_type);
      }
      return typeid(ValueType);
    }());
    static std::unordered_map<std::type_index, DataType> typeid_to_dt{
        {std::type_index(typeid(int16_t)), DataType::INT16},
        {std::type_index(typeid(int32_t)), DataType::INT32},
        {std::type_index(typeid(float)), DataType::FLOAT},
        {std::type_index(typeid(double)), DataType::DOUBLE}};

    return typeid_to_dt.at(type);
  };

  const T* getTypedBuffer() const { return static_cast<const T*>(getBuffer()); };
  T* getTypedBuffer() { return static_cast<T*>(getBuffer()); };

  ~IRawData() override = default;
};

template <typename DataType>
class RawDataVector final : public IRawData<DataType> {
 public:
  explicit RawDataVector(std::vector<DataType>&& vector) : _vector(std::move(vector)) {}
  explicit RawDataVector(size_t size) : _vector(size) {}
  ~RawDataVector() override = default;

  const void* getBuffer() const override { return _vector.data(); }
  void* getBuffer() override { return _vector.data(); }
  size_t getSize() const override { return _vector.size(); }

 private:
  std::vector<DataType> _vector;
};

template <typename DataType>
class RawDataNoInit final : public IRawData<DataType> {
 public:
  explicit RawDataNoInit(size_t size) : _buffer(std::make_unique<DataType[]>(size)), _size(size) {}
  ~RawDataNoInit() override = default;

  const void* getBuffer() const override { return _buffer.get(); }
  void* getBuffer() override { return _buffer.get(); }
  size_t getSize() const override { return _size; }

 private:
  std::unique_ptr<DataType[]> _buffer;
  size_t _size;
};

template <typename DataType>
class RawDataWeak : public IRawData<DataType> {
 public:
  RawDataWeak(void* buffer, size_t size) : _buffer(buffer), _size(size) {}
  ~RawDataWeak() override = default;

  const void* getBuffer() const override { return _buffer; }
  void* getBuffer() override { return _buffer; }
  size_t getSize() const override { return _size; }

 protected:
  void* _buffer;
  size_t _size;
};

template <typename DataType>
class RawDataStream : public IRawData<DataType> {
 public:
  RawDataStream(size_t size) : _size(size) {}
  ~RawDataStream() override = default;

  const void* getBuffer() const override {
    throw std::runtime_error(__FUNCTION__);
    return nullptr;
  }
  void* getBuffer() override {
    throw std::runtime_error(__FUNCTION__);
    return nullptr;
  }
  size_t getSize() const override { return _size; }

 protected:
  size_t _size;
};

}  // namespace urx
