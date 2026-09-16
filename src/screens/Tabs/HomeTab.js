import { useEffect, useState } from 'react';
import { Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function HomeTab() {
  const [selectedYear, setSelectedYear] = useState('2026');
  const [stats, setStats] = useState({ confirmados: 'Carregando...', suspeitas: 'Carregando...' });
  const anos = ['2026', '2025', '2024'];

  // Equivalente ao carregar_dados_api e cache do Python
  useEffect(() => {
    carregarDados(selectedYear);
  }, [selectedYear]);

  const carregarDados = async (ano) => {
    setStats({ confirmados: '...', suspeitas: '...' });
    try {
      const response = await fetch(`${API_URL}/api/estatisticas/?ano=${ano}`, {
        headers: {
          'ngrok-skip-browser-warning': 'true',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        const resumo = result.resumo || {};
        
        setStats({
          confirmados: String(resumo.total_casos_positivos || 0),
          suspeitas: String(resumo.total_casos_suspeitos || 0)
        });
      } else {
        setStats({ confirmados: 'Erro', suspeitas: 'Erro' });
      }
    } catch (error) {
      setStats({ confirmados: 'Erro', suspeitas: 'Erro' });
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      
      {/* Filtro de Anos Horizontal */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.yearScroll}>
        {anos.map((ano) => (
          <TouchableOpacity
            key={ano}
            style={[styles.yearButton, selectedYear === ano ? styles.yearButtonSelected : styles.yearButtonUnselected]}
            onPress={() => setSelectedYear(ano)}
          >
            <Text style={[styles.yearText, selectedYear === ano ? styles.yearTextSelected : styles.yearTextUnselected]}>
              {ano}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Cards de Estatísticas */}
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Text style={styles.cardTitle}>Casos confirmados</Text>
          <Text style={styles.cardValue}>{stats.confirmados}</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.cardTitle}>Suspeitas de dengue</Text>
          <Text style={styles.cardValue}>{stats.suspeitas}</Text>
        </View>
      </View>

      {/* Gráficos / Cards informativos */}
      <View style={styles.chartCard}>
        <Text style={styles.chartTitle}>Casos confirmados por mês</Text>
        <Image source={require('../../../assets/images/grafico1.png')} style={styles.chartImage} resizeMode="contain" />
      </View>

      <View style={styles.chartCard}>
        <Text style={styles.chartTitle}>Proporção de focos por tipo</Text>
        <Image source={require('../../../assets/images/grafico2.png')} style={styles.chartImage} resizeMode="contain" />
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  contentContainer: { padding: 15, paddingBottom: 100 },
  yearScroll: { marginBottom: 15 },
  yearButton: {
    width: 80,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  yearButtonSelected: { backgroundColor: '#000' },
  yearButtonUnselected: { backgroundColor: '#E0E0E0' },
  yearText: { fontSize: 14, fontWeight: 'bold' },
  yearTextSelected: { color: '#FFF' },
  yearTextUnselected: { color: '#000' },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFF',
    padding: 15,
    borderRadius: 10,
    elevation: 1,
    marginHorizontal: 5,
    height: 100,
    justifyContent: 'space-between',
  },
  cardTitle: { fontSize: 13, fontWeight: 'bold', color: '#333' },
  cardValue: { fontSize: 24, fontWeight: 'bold', color: '#000' },
  chartCard: {
    backgroundColor: '#FFF',
    padding: 15,
    borderRadius: 10,
    elevation: 1,
    marginBottom: 15,
    height: 280,
    justifyContent: 'space-between',
  },
  chartTitle: { fontSize: 16, fontWeight: 'bold', color: '#000', marginBottom: 10 },
  chartImage: { width: '100%', height: '85%' },
});