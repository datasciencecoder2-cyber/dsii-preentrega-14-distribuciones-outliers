"""Pruebas de la calidad del EDA; correr con python -m unittest discover -s tests -v."""
import unittest
from pathlib import Path
import pandas as pd
from src.eda import cargar_datos, marcar_iqr, resumen_descriptivo

ROOT = Path(__file__).resolve().parents[1]


class TestPreentrega14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=cargar_datos(ROOT / "datos" / "tips.csv")

    def test_01_244_filas_y_siete_variables_originales(self):
        self.assertEqual(self.df.shape, (244, 8))  # más registro_ref sintético

    def test_02_sin_nulos(self):
        self.assertEqual(int(self.df.isna().sum().sum()),0)

    def test_03_categorias_observadas(self):
        self.assertEqual(set(self.df.day.astype(str)),{'Thur','Fri','Sat','Sun'})

    def test_04_medidas_numericas_y_curtosis(self):
        e=resumen_descriptivo(self.df)
        self.assertEqual(len(e),3)
        self.assertTrue(e['curtosis_exceso'].notna().all())
        self.assertTrue(e['asimetria'].notna().all())

    def test_05_iqr_cuenta(self):
        _,r=marcar_iqr(self.df,'total_bill')
        self.assertAlmostEqual(r['limite_superior'],40.2975,places=3)
        self.assertEqual(r['n_atipicos'],9)

    def test_06_iqr_propina(self):
        _,r=marcar_iqr(self.df,'tip')
        self.assertAlmostEqual(r['limite_superior'],5.90625,places=4)
        self.assertEqual(r['n_atipicos'],9)

    def test_07_atipicos_solapados(self):
        x,_=marcar_iqr(self.df,'total_bill')
        x,_=marcar_iqr(x,'tip')
        self.assertEqual(int((x.outlier_total_bill & x.outlier_tip).sum()),3)
        self.assertEqual(int((x.outlier_total_bill | x.outlier_tip).sum()),15)

    def test_08_una_fila_por_registro(self):
        self.assertTrue(self.df.registro_ref.is_unique)
        self.assertEqual(self.df.registro_ref.iloc[0],1)

    def test_09_no_elimina_duplicados_sin_id_real(self):
        self.assertEqual(int(self.df.drop(columns='registro_ref').duplicated().sum()),1)

    def test_10_no_modifica_entrada(self):
        original=self.df.copy(deep=True)
        resultado,_=marcar_iqr(self.df,'tip')
        pd.testing.assert_frame_equal(original,self.df)
        self.assertIn('outlier_tip',resultado.columns)
        self.assertNotIn('outlier_tip',self.df.columns)

    def test_11_rechaza_esquema_incompleto(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'invalido.csv'
            pd.DataFrame({'total_bill':[11]}).to_csv(p,index=False)
            with self.assertRaises(ValueError): cargar_datos(p)

    def test_12_rechaza_factor_ilegal(self):
        with self.assertRaises(ValueError): marcar_iqr(self.df,'tip',0)


if __name__ == '__main__': unittest.main()
