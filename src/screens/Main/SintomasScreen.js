import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function SintomasScreen({ navigation }) {
  // Lista 1: Principais Sintomas
  const principaisSintomas = [
    { id: '1', text: 'Febre', image: require('../../../assets/images/termometro.png') },
    { id: '2', text: 'Dores no corpo e/ ou articulações', image: require('../../../assets/images/dores.jpeg') },
    { id: '3', text: 'Enjoo e/ou dores na barriga', image: require('../../../assets/images/enjoo.jpg') },
    { id: '4', text: 'Dor de cabeça e/ou atrás dos olhos', image: require('../../../assets/images/dor-cabeca.jpg') },
    { id: '5', text: 'Manchas vermelhas na pele', image: require('../../../assets/images/manchas.jpeg') },
    { id: '6', text: 'Fraqueza, cansaço e falta de energia', image: require('../../../assets/images/fraqueza.png') },
  ];

  // Lista 2: Sinais de Alerta
  const sinaisAlerta = [
    { id: '7', text: 'Cansaço intenso', image: require('../../../assets/images/cansaco.jpg') },
    { id: '8', text: 'Dor forte na barriga', image: require('../../../assets/images/dor-barriga.jpg') },
    { id: '9', text: 'Dificuldade para respirar', image: require('../../../assets/images/respirar.jpg') },
    { id: '10', text: 'Vômitos', image: require('../../../assets/images/vomitos.jpg') },
    { id: '11', text: 'Tontura / sensação de desmaio', image: require('../../../assets/images/tontura.png') },
    { id: '12', text: 'Sangramento no nariz, gengiva e/ou fezes', image: require('../../../assets/images/sangramento.jpg') },
  ];

  // Componente que renderiza cada Card
  const renderCard = (item) => (
    <View key={item.id} style={styles.card}>
      <Image source={item.image} style={styles.cardImage} />
      <View style={styles.cardTextContainer}>
        <Text style={styles.cardText} numberOfLines={3}>{item.text}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* CABEÇALHO DEGRADÊ (Igual ao TabNavigator e Home) */}
      <LinearGradient 
        colors={['#3AC0ED', '#72FC90']} 
        start={{ x: 0, y: 0 }} 
        end={{ x: 1, y: 0 }} 
        style={styles.header}
      >
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <MaterialCommunityIcons name="arrow-left" size={26} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Sintomas</Text>
      </LinearGradient>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        
        {/* BOX INFORMATIVO */}
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            Ao sentir alguns desses sintomas, procure atendimento médico. Evite a automedicação.
          </Text>
        </View>

        {/* SEÇÃO 1: PRINCIPAIS SINTOMAS */}
        <Text style={styles.sectionTitle}>Principais sintomas da Dengue:</Text>
        <View style={styles.gridContainer}>
          {principaisSintomas.map(renderCard)}
        </View>

        {/* SEÇÃO 2: SINAIS DE ALERTA */}
        <Text style={styles.sectionTitle}>Sinais de alerta:</Text>
        <View style={styles.gridContainer}>
          {sinaisAlerta.map(renderCard)}
        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  header: {
    height: 90,
    paddingTop: 45, // Espaço para a barra de status do celular
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: { marginRight: 15 },
  headerTitle: { fontSize: 22, fontWeight: 'bold', color: '#000' },
  
  scrollContent: { padding: 15, paddingBottom: 50 },
  
  infoBox: {
    backgroundColor: '#E0F7FA', // Azul claro correspondente ao do Kivy
    padding: 15,
    borderRadius: 15,
    marginBottom: 20,
  },
  infoText: { fontSize: 14, fontWeight: 'bold', color: '#333', textAlign: 'center' },
  
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#000', marginBottom: 15, marginTop: 10 },
  
  // O truque para simular o GridLayout de 3 colunas
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  
  card: {
    width: '31%', // Deixa espaço para o respiro entre os 3 itens
    height: 130, // Mesma altura aproximada do Kivy
    backgroundColor: '#FFF',
    borderRadius: 12,
    elevation: 2, // Sombra no Android
    shadowColor: '#000', // Sombra no iOS
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    marginBottom: 15,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  cardImage: {
    width: '100%',
    height: '75%', // Ocupa a maior parte do topo
    resizeMode: 'cover',
  },
  cardTextContainer: {
    height: '25%',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 2,
    paddingTop: 2,
  },
  cardText: {
    fontSize: 10,
    textAlign: 'center',
    color: '#000',
    fontWeight: '500',
  },
});