import unittest
import pandas as pd

from scripts.common_pipeline import build_core


class TestBrasilCore(unittest.TestCase):
    def test_estado_y_categoria_e_informalidad(self):
        df = pd.DataFrame(
            {
                "UF": [11, 11, 11, 11],
                "UPA": [1, 1, 1, 1],
                "V1008": [1, 1, 1, 1],
                "V1014": [1, 1, 1, 1],
                "V2003": [1, 2, 3, 4],
                "V1028": [1.0, 1.0, 1.0, 1.0],
                "VD4002": [1, 2, None, 1],
                "VD4009": [2, 9, 10, 5],
                "VD4012": [1, 2, None, 2],
                "V4018": [1, 1, 1, 1],
            }
        )

        out = build_core("brasil", 2018, 1, df)

        self.assertListEqual(out["ocupado"].tolist(), [1, 0, 0, 1])
        self.assertListEqual(out["desocupado"].tolist(), [0, 1, 0, 0])
        self.assertListEqual(out["inactivo"].tolist(), [0, 0, 1, 0])

        # VD4009: 2 y 5 son asalariados; 9 cuentapropia; 10 no
        self.assertListEqual(out["asalariado"].tolist(), [1, 0, 0, 1])
        self.assertListEqual(out["cuentapropia"].tolist(), [0, 1, 0, 0])

        # informal: asalariado sin carteira (2/4/6) o cuentapropia con VD4012==2
        self.assertListEqual(out["informal"].tolist(), [1, 1, 0, 0])
        self.assertListEqual(out["formal"].tolist(), [0, 0, 1, 1])


if __name__ == "__main__":
    unittest.main()
