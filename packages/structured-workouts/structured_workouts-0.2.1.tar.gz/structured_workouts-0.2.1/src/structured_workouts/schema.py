from typing import List, Self

from .validation import ValidationMixin
from .base import BaseWorkout, ConstantValue, Instruction, Interval, RampValue, RangeValue, Repeat, Section, Value, Reference


class Workout(BaseWorkout, ValidationMixin):
    def _range_to_mean(self, item: Interval) -> Interval:
        if isinstance(item.volume, RangeValue):
            # Calculate mean from min and max values if they're absolute
            min_val = item.volume.min.value if item.volume.min and item.volume.min.reference == Reference.absolute else 0
            max_val = item.volume.max.value if item.volume.max and item.volume.max.reference == Reference.absolute else 0
            mean_val = (min_val + max_val) / 2 if item.volume.min and item.volume.max else (min_val or max_val)
            
            item.volume = ConstantValue(
                quantity=item.volume.quantity,
                value=Value(reference=Reference.absolute, value=mean_val)
            )

        if isinstance(item.intensity, RangeValue):
            # Calculate mean from min and max values if they're absolute
            min_val = item.intensity.min.value if item.intensity.min and item.intensity.min.reference == Reference.absolute else 0
            max_val = item.intensity.max.value if item.intensity.max and item.intensity.max.reference == Reference.absolute else 0
            mean_val = (min_val + max_val) / 2 if item.intensity.min and item.intensity.max else (min_val or max_val)
            
            item.intensity = ConstantValue(
                quantity=item.intensity.quantity,
                value=Value(reference=Reference.absolute, value=mean_val)
            )

        return item

    def _flatten_item(self, item, *, repeat_count=1, range_to_mean: bool = False) -> List[Interval]:
        if isinstance(item, Interval):
            if range_to_mean:
                return [self._range_to_mean(item)] * repeat_count
            else:
                return [item] * repeat_count
        elif isinstance(item, Repeat):
            # Get the count value, assuming it's a constant value for now
            count = int(item.count.value.value) if isinstance(item.count, ConstantValue) and item.count.value.reference == Reference.absolute else 1
            flattened = []
            # Repeat the sequence count times
            for _ in range(count):
                for content_item in item.content:
                    if not isinstance(content_item, Instruction):
                        flattened.extend(self._flatten_item(content_item, repeat_count=1, range_to_mean=range_to_mean))
            return flattened
        elif isinstance(item, Section):
            flattened = []
            for content_item in item.content:
                if not isinstance(content_item, Instruction):
                    flattened.extend(self._flatten_item(content_item, repeat_count=1, range_to_mean=range_to_mean))
            return flattened
        return []

    def flattened_intervals(self, range_to_mean: bool = False) -> Self:
        """Recursively flatten the workout into a list of intervals."""

        intervals = []
        for item in self.content:
            if not isinstance(item, Instruction):
                intervals.extend(self._flatten_item(item, range_to_mean=range_to_mean))
        return intervals

Repeat.model_rebuild()
Section.model_rebuild()