from flax import linen as nn
from jax import numpy as jnp
from flax.typing import Array, Initializer
from typing import Optional
import einops as eo


class Attn(nn.Module):
    @nn.compact
    def __call__(
        self, q: Array, k: Array, v: Array, mask: Optional[Array] = None
    ) -> Array:
        dims = q.shape[-1]

        scores = jnp.einsum("... j k, ... i k -> ... j i", q, k)
        scores /= dims
        if mask is not None:
            scores = jnp.where(mask, scores, -jnp.inf)
        scores = nn.softmax(scores)
        out = jnp.einsum("... j k, ... k i -> ... j i", scores, v)
        return out


class GroupedQuaryAttention(nn.Module):
    dim: int
    num_qheads: int
    num_kvheads: int
    use_bias: bool = True
    kernel_init: Initializer = nn.initializers.lecun_normal()
    bias_init: Initializer = nn.initializers.zeros_init()

    @nn.compact
    def __call__(
        self,
        q: Array,
        k: Optional[Array] = None,
        v: Optional[Array] = None,
        mask: Optional[Array] = None,
    ) -> Array:
        assert self.num_qheads % self.num_kvheads == 0, (
            "num of kv heads must by divisible by num of q heads"
        )
        assert self.dim % self.num_qheads == 0, (
            "dims must be devisible by num of q heads"
        )

        in_dim = q.shape[-1]

        head_dim = self.dim // self.num_qheads

        def linear(x, heads):
            x = nn.Dense(
                heads * head_dim,
                use_bias=self.use_bias,
                kernel_init=self.kernel_init,
                bias_init=self.bias_init,
            )(x)
            x = eo.rearrange(x, "... (i j) -> ... i j", i=heads)
            return x

        if not k:
            k = q
        if not v:
            v = k

        qx = linear(q, self.num_qheads)
        kx = linear(k, self.num_kvheads)
        vx = linear(v, self.num_kvheads)

        qx = eo.rearrange(vx, "... i j k -> ... j i k")
        kx = eo.repeat(
            kx, "... i j k -> ... (j r) i k", r=self.num_qheads // self.num_kvheads
        )
        vx = eo.repeat(
            vx, "... i j k -> ... (j r) i k", r=self.num_qheads // self.num_kvheads
        )

        out = Attn()(qx, kx, vx, mask)

        out = eo.rearrange(out, "... i j k -> ... j (i k)")
        out = nn.Dense(
            in_dim,
            use_bias=self.use_bias,
            kernel_init=self.kernel_init,
            bias_init=self.bias_init,
        )(out)

        return out


class MultiHeadAttention(nn.Module):
    dim: int
    num_heads: int
    use_bias: bool = True
    kernel_init: Initializer = nn.initializers.lecun_normal()
    bias_init: Initializer = nn.initializers.zeros_init()

    @nn.compact
    def __call__(
        self,
        q: Array,
        k: Optional[Array] = None,
        v: Optional[Array] = None,
        mask: Optional[Array] = None,
    ) -> Array:
        return GroupedQuaryAttention(
            self.dim,
            self.num_heads,
            self.num_heads,
            self.use_bias,
            self.kernel_init,
            self.bias_init,
        )(q, k, v, mask)


class Attention(nn.Module):
    dim: int
    use_bias: bool = True
    kernel_init: Initializer = nn.initializers.lecun_normal()
    bias_init: Initializer = nn.initializers.zeros_init()

    @nn.compact
    def __call__(
        self,
        q: Array,
        k: Optional[Array] = None,
        v: Optional[Array] = None,
        mask: Optional[Array] = None,
    ) -> Array:
        return MultiHeadAttention(
            self.dim, 1, self.use_bias, self.kernel_init, self.bias_init
        )(q, k, v, mask)
