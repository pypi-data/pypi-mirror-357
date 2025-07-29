"""Construct sampling functions for each model parameter."""

import abc
import lhs
import numpy as np

from .build import lookup


class Base(abc.ABC):
    """
    The base class for parameter samplers.
    """

    @abc.abstractmethod
    def draw_samples(self, settings, prng, particles, prior, sampled):
        """
        Return samples from the model prior distribution.

        :param settings: A dictionary of sampler-specific settings.
        :param prng: The source of randomness for the sampler.
        :param particles: The number of particles.
        :param prior: The prior distribution table.
        :param sampled: Sampled values for specific parameters.
        """
        pass


class LatinHypercube(Base):
    """
    Draw parameter samples using Latin hypercube sampling.
    """

    def draw_samples(self, settings, prng, particles, prior, sampled):
        """
        Return samples from the model prior distribution.

        :param settings: A dictionary of sampler-specific settings.
        :param prng: The source of randomness for the sampler.
        :param particles: The number of particles.
        :param prior: The prior distribution table.
        :param sampled: Sampled values for specific parameters.
        """
        # Separate the independent and dependent parameters.
        indep_params = {
            name: dist
            for (name, dist) in prior.items()
            if not dist.get('dependent', False)
        }
        dep_params = {
            name: dist
            for (name, dist) in prior.items()
            if dist.get('dependent', False)
        }

        # Convert list arguments into numpy arrays.
        for table in [indep_params, dep_params]:
            for dist in table.values():
                args = dist.get('args', {})
                arg_names = list(args.keys())
                for arg_name in arg_names:
                    if isinstance(args[arg_name], list):
                        args[arg_name] = np.array(args[arg_name])

        dep_fn = settings.get('dependent_distributions_function')
        if dep_fn is None:
            if dep_params:
                raise ValueError('dependent_distributions_function missing')
            dep_params = None
        elif isinstance(dep_fn, str):
            # Turn a function name into the corresponding function.
            dep_fn = lookup(dep_fn)

        return lhs.draw(
            prng,
            particles,
            indep_params,
            dep_params=dep_params,
            dep_fn=dep_fn,
            values=sampled,
        )
