import { MaterialCommunityIcons } from '@expo/vector-icons';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function SintomasScreen({ navigation }) {
  // Lista de sintomas mapeados do projeto original
  const listaSintomas = [
    { id: '1', titulo: 'Febre alta', descricao: 'Febre de início abrupto, geralmente acima de 38.5°C.', icone: 'thermometer' },
    { id: '2', titulo: 'Dores no corpo', descricao: 'Dores intensas nos ossos, articulações e músculos.', icone: 'bone' },
    { id: '3', titulo: 'Dor de cabeça', descricao: 'Dor forte na região frontal e atrás dos olhos.', icone: 'head-outline' },
    { id: '4', titulo: 'Tontura e fraqueza', descricao: 'Sensação de desequilíbrio e cansaço excessivo.', icone: 'flash-off' },
    { id: '5', titulo: 'Enjoo e vômitos', descricao: 'Náuseas frequentes e perda de apetite.', icone: 'emoticon-sick-outline' },
    { id: '6', titulo: 'Manchas vermelhas', descricao: 'Erupções cutâneas que podem coçar pelo corpo.', icone: 'dots-hexagon' },
  ];

  return (
    <View style={styles.container}>
      {/* Cabeçalho Interno */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <MaterialCommunityIcons name="arrow-left" size={24} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Sintomas da Dengue</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.sectionSubtitle}>
          Fique atento aos sinais. Caso apresente alguns deles, procure uma unidade de saúde.
        </Text>

        {listaSintomas.map((item) => (
          <View key={item.id} style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name={item.icone} size={28} color="#1D76D2" />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.cardTitle}>{item.titulo}</Text>
              <Text style={styles.cardDescription}>{item.descricao}</Text>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  header: {
    height: 90,
    paddingTop: 35,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  backButton: { marginRight: 15 },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#000' },
  scrollContent: { padding: 20, paddingBottom: 40 },
  sectionSubtitle: { fontSize: 14, color: '#666', marginBottom: 20, lineHeight: 20 },
  card: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    padding: 15,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: 'center',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#E2F7F9',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  textContainer: { flex: 1 },
  cardTitle: { fontSize: 16, fontWeight: 'bold', color: '#000', marginBottom: 4 },
  cardDescription: { fontSize: 13, color: '#666', lineHeight: 18 },
});