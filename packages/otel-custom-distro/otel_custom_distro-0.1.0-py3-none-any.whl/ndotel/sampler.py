from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision

class MySampler(Sampler):
    def should_sample(self, parent_context, trace_id, name, kind, attributes, links):
        if "skip" in name:
            return SamplingResult(Decision.DROP)
        return SamplingResult(Decision.RECORD_AND_SAMPLE)

    def get_description(self):
        return "MySampler"

