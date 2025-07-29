#pragma once

#include <memory>
#include <type_traits>

namespace uac {

struct IGroup;
struct Group;
struct Excitation;
struct SuperGroup;

template <typename T>
inline std::enable_if_t<std::is_same_v<IGroup, T> || std::is_same_v<SuperGroup, T> ||
                            std::is_same_v<Excitation, T> || std::is_same_v<Group, T>,
                        bool>
operator==(const std::shared_ptr<T>& lhs, const std::shared_ptr<T>& rhs) {
  return (lhs && rhs) ? (*lhs == *rhs) : (!!lhs == !!rhs);
}

template <typename T>
inline std::enable_if_t<std::is_same_v<IGroup, T> || std::is_same_v<SuperGroup, T> ||
                            std::is_same_v<Excitation, T> || std::is_same_v<Group, T>,
                        bool>
operator==(const std::weak_ptr<T>& lhs, const std::weak_ptr<T>& rhs) {
  auto lhs_lock = lhs.lock();
  auto rhs_lock = rhs.lock();

  return (lhs_lock && rhs_lock) ? (lhs_lock == rhs_lock) : (!!lhs_lock == !!rhs_lock);
}

}  // namespace uac