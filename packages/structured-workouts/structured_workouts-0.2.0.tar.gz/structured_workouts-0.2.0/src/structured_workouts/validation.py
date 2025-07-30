from typing import Iterator, List, Set

from .base import Interval, Repeat, Section, ConstantValue, RangeValue, RampValue


class ValidationMixin:
    def _iter_content(self, item: Repeat | Section | None = None) -> Iterator[Interval]:
        if item is None:
            item = self

        for item in item.content:
            yield item
            if isinstance(item, (Section, Repeat)):
                yield from self._iter_content(item)
    
    def intervals(self) -> Iterator[Interval]:
        for item in self._iter_content():
            if isinstance(item, Interval):
                yield item

    def repeats(self) -> Iterator[Repeat]:
        for item in self._iter_content():
            if isinstance(item, Repeat):
                yield item
    
    def _get_value_attributes(self, value_specification: ConstantValue | RangeValue | RampValue) -> List[str]:
        match value_specification.type:
            case "constant":
                return ["value"]
            case "range":
                return ["min", "max"]
            case "ramp":
                return ["start", "end"]
            case _:
                raise ValueError(f"Unknown value type: {value_specification.type}")
    
    def get_repeat_variables(self) -> Set[str]:
        variables = set()
        for repeat in self.repeats():
            if repeat.count.type == "constant" and repeat.count.value.reference == "parameter":
                variables.add(repeat.count.value.parameter)
            elif repeat.count.type == "range":
                if repeat.count.min and repeat.count.min.reference == "parameter":
                    variables.add(repeat.count.min.parameter)
                if repeat.count.max and repeat.count.max.reference == "parameter":
                    variables.add(repeat.count.max.parameter)

        return variables
    
    def _value_specification_has_default(self, value_specification: ConstantValue | RangeValue | RampValue) -> bool:
        match value_specification.type:
            case "constant":
                return value_specification.value.reference == "absolute"
            case "range":
                has_min = value_specification.min and value_specification.min.reference == "absolute"
                has_max = value_specification.max and value_specification.max.reference == "absolute"
                return has_min or has_max
            case "ramp":
                return (value_specification.start.reference == "absolute" and 
                        value_specification.end.reference == "absolute")
    
    def _get_interval_variables(self, interval_attribute: str, ignore_with_default: bool = False) -> Set[str]:
        variables = set()
        for interval in self.intervals():
            volume_or_intensity = getattr(interval, interval_attribute)

            # Extract variables from the value specification
            def add_variables_from_value(value):
                if value and value.reference == "parameter":
                    variables.add(value.parameter)

            match volume_or_intensity.type:
                case "constant":
                    if ignore_with_default and self._value_specification_has_default(volume_or_intensity):
                        continue
                    add_variables_from_value(volume_or_intensity.value)
                case "range":
                    if ignore_with_default and self._value_specification_has_default(volume_or_intensity):
                        continue
                    add_variables_from_value(volume_or_intensity.min)
                    add_variables_from_value(volume_or_intensity.max)
                case "ramp":
                    if ignore_with_default and self._value_specification_has_default(volume_or_intensity):
                        continue
                    add_variables_from_value(volume_or_intensity.start)
                    add_variables_from_value(volume_or_intensity.end)

        return variables

    def get_intensity_variables(self, ignore_with_default: bool = False) -> Set[str]:
        return self._get_interval_variables("intensity", ignore_with_default=ignore_with_default)

    def get_volume_variables(self, ignore_with_default: bool = False) -> Set[str]:
        return self._get_interval_variables("volume", ignore_with_default=ignore_with_default)
    
    def get_variables(self) -> Set[str]:
        pass

    def has_only_one_intensity_variable(self, allow_absolute: bool = False) -> bool:
        """
        Check if intensity in the workout is always specified as a variable, and if it is only one variable.
        """
        variables = set()
        
        for interval in self.intervals():
            intensity = interval.intensity
            has_variable = False

            def check_value_for_variable(value):
                nonlocal has_variable
                if value and value.reference == "parameter":
                    variables.add(value.parameter)
                    has_variable = True

            match intensity.type:
                case "constant":
                    check_value_for_variable(intensity.value)
                case "range":
                    check_value_for_variable(intensity.min)
                    check_value_for_variable(intensity.max)
                case "ramp":
                    check_value_for_variable(intensity.start)
                    check_value_for_variable(intensity.end)

            if not has_variable and not allow_absolute:
                return False

        if len(variables) > 1:
            return False
                    
        return True

    def has_only_absolute_intensity(self) -> bool:
        """
        Check if intensity in the workout is always specified as a fixed value, and not as a variable.
        """
        for interval in self.intervals():
            intensity = interval.intensity

            def has_parameter_reference(value):
                return value and value.reference == "parameter"

            match intensity.type:
                case "constant":
                    if has_parameter_reference(intensity.value):
                        return False
                case "range":
                    if (has_parameter_reference(intensity.min) or 
                        has_parameter_reference(intensity.max)):
                        return False
                case "ramp":
                    if (has_parameter_reference(intensity.start) or 
                        has_parameter_reference(intensity.end)):
                        return False
                    
        return True
    
    def has_only_one_intensity_quantity(self) -> bool:
        """
        Check if intensity in the workout is always specified with the same quantity, and not as a variable.
        """
        quantities = set()

        for interval in self.intervals():
            quantities.add(interval.intensity.quantity)

        if len(quantities) > 1:
            return False

        return True
    
    def has_only_one_volume_quantity(self) -> bool:
        """
        Check if volume in the workout is always specified with the same quantity, and not as a variable.
        """
        quantities = set()

        for interval in self.intervals():
            quantities.add(interval.volume.quantity)

        if len(quantities) > 1:
            return False

        return True
    
    def repeats_are_fixed(self) -> bool:
        """
        Check if repeats are always specified as a fixed value.
        """
        for repeat in self.repeats():
            if repeat.count.type != "constant":
                return False
            if repeat.count.value.reference == "parameter":
                return False
        return True
    
    def volume_is_duration(self) -> bool:
        """
        Check if volume is always specified as duration.
        """
        for interval in self.intervals():
            if interval.volume.quantity != "duration":
                return False
        return True
    
    def intensity_is_power(self) -> bool:
        """
        Check if intensity is always specified as power.
        """
        for interval in self.intervals():
            if interval.intensity.quantity != "power":
                return False
        return True