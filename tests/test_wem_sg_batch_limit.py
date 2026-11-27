"""Regression coverage for WEM-SG read batch compatibility."""

import asyncio
import unittest
from unittest.mock import AsyncMock

from custom_components.weishaupt_wtc_lan.api import (
    WeishauptApiClient,
)
from custom_components.weishaupt_wtc_lan.const import (
    CMD_ERROR,
    CMD_RESPONSE,
)


class TestWemSgBatchLimit(unittest.TestCase):
    """Ensure reads avoid the unreliable sixth request slot."""

    def test_read_batches_never_use_sixth_slot(self):
        """Read all parameters using batches of at most five."""

        async def run():
            client = WeishauptApiClient(
                "127.0.0.1", "test", "test"
            )
            batch_sizes = []

            async def mock_post(payload):
                request = payload["CAPI"]
                batch_sizes.append(request["NN"])

                response = {"NN": request["NN"]}

                for key, frame in request.items():
                    if key == "NN":
                        continue

                    vg = frame["VG"]

                    # Simulate a gateway that rejects slot N06.
                    if key == "N06":
                        response[key] = {
                            "VG": (
                                f"{CMD_ERROR:02x}"
                                + vg[2:12]
                                + "0002"
                                + "0001"
                            )
                        }
                        continue

                    response[key] = {
                        "VG": (
                            f"{CMD_RESPONSE:02x}"
                            + vg[2:16]
                            + "32"
                        )
                    }

                return {"CAPI": response}

            client._post = AsyncMock(side_effect=mock_post)

            params = [
                {
                    "key": f"sensor_{i}",
                    "mi": 0x09,
                    "mx": 0x01,
                    "ox": 0x2600 + i,
                    "os": 0x02,
                    "vs": 1,
                }
                for i in range(13)
            ]

            try:
                results = await client.read_parameters(params)

                self.assertEqual(batch_sizes, [5, 5, 3])
                self.assertEqual(
                    set(results),
                    {param["key"] for param in params},
                )
                self.assertEqual(client.last_read_failed_batches, 0)

                for result in results.values():
                    self.assertEqual(result["value_int"], 50)
            finally:
                await client.close()

        asyncio.run(run())
