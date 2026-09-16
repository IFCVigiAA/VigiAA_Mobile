import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function NewTab({ navigation }) {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <Text style={styles.headerTitle}>Cadastro</Text>

      {/* CARD 1: FOCO DE DENGUE */}
      <TouchableOpacity 
        style={styles.card} 
        activeOpacity={0.9}
        onPress={() => navigation.navigate('FormFoco')}
      >
        <Image 
          source={require('../../../assets/images/focos.jpg')} 
          style={styles.cardImage} 
        />
        <View style={styles.cardContent}>
          <View style={styles.textContainer}>
            <Text style={styles.cardTitle}>Cadastrar novo foco</Text>
            <Text style={styles.cardDescription}>Forneça informações sobre focos do mosquito.</Text>
          </View>
          <View style={styles.plusButton}>
            <MaterialCommunityIcons name="plus" size={24} color="#FFF" />
          </View>
        </View>
      </TouchableOpacity>

      {/* CARD 2: CASO SUSPEITO */}
      <TouchableOpacity 
        style={styles.card} 
        activeOpacity={0.9}
        onPress={() => navigation.navigate('FormCaso')}
      >
        <Image 
          source={require('../../../assets/images/paciente.jpg')} 
          style={styles.cardImage} 
        />
        <View style={styles.cardContent}>
          <View style={styles.textContainer}>
            <Text style={styles.cardTitle}>Cadastrar caso suspeito</Text>
            <Text style={styles.cardDescription}>Forneça informações para o cadastro de um paciente suspeito.</Text>
          </View>
          <View style={styles.plusButton}>
            <MaterialCommunityIcons name="plus" size={24} color="#FFF" />
          </View>
        </View>
      </TouchableOpacity>

      {/* CARD 3: CASO POSITIVO */}
      <TouchableOpacity 
        style={styles.card} 
        activeOpacity={0.9}
        onPress={() => navigation.navigate('FormCasoPositivo')}
      >
        <Image 
          source={require('../../../assets/images/agentes.jpeg')} 
          style={styles.cardImage} 
        />
        <View style={styles.cardContent}>
          <View style={styles.textContainer}>
            <Text style={styles.cardTitle}>Cadastrar caso positivo</Text>
            <Text style={styles.cardDescription}>Registre um diagnóstico confirmado de dengue.</Text>
          </View>
          <View style={styles.plusButton}>
            <MaterialCommunityIcons name="plus" size={24} color="#FFF" />
          </View>
        </View>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  contentContainer: { padding: 20, paddingBottom: 100 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#000', marginBottom: 20 },
  card: {
    height: 260,
    backgroundColor: '#FFF',
    borderRadius: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    marginBottom: 20,
    overflow: 'hidden',
  },
  cardImage: { width: '100%', height: '55%' },
  cardContent: {
    height: '45%',
    paddingHorizontal: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  textContainer: { flex: 1, paddingRight: 10 },
  cardTitle: { fontSize: 17, fontWeight: 'bold', color: '#000', marginBottom: 4 },
  cardDescription: { fontSize: 13, color: '#666' },
  plusButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#3AC0ED',
    alignItems: 'center',
    justifyContent: 'center',
  },
});