import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { useState } from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

const LINK_COLOR = "#0077B6";

export default function ExploreTab({ navigation }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      
      {/* CARD DO CARROSSEL / BANNER */}
      <View style={styles.swiperContainer}>
        <Image 
          source={require('../../../assets/images/banner1.jpeg')} // Ajuste o caminho conforme seus assets
          style={styles.bannerImage} 
        />
        <View style={styles.bannerOverlay}>
          <Text style={styles.bannerText}>O mosquito não descansa!</Text>
        </View>
      </View>

      {/* BOX INFORMATIVO EXPANSÍVEL */}
      <View style={styles.infoBox}>
        <Text style={styles.infoText}>
          A <Text style={{ fontWeight: 'bold' }}>dengue</Text> é uma arbovirose{' '}
          {isExpanded 
            ? "causada pelo mosquito Aedes aegypti. " 
            : "... "}
          <Text 
            style={{ color: LINK_COLOR, fontWeight: 'bold' }}
            onPress={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? "ler menos" : "ler mais..."}
          </Text>
        </Text>
      </View>

      {/* LISTA DE OPÇÕES / AÇÕES */}
      <View style={styles.listContainer}>
        
        {/* Item Sintomas */}
        <TouchableOpacity 
          style={styles.listItem} 
          onPress={() => navigation.navigate('Sintomas')}
        >
          <View style={styles.listLeft}>
            <MaterialCommunityIcons name="thermometer" size={24} color="#333" style={styles.listIcon} />
            <View>
              <Text style={styles.listTitle}>Sintomas</Text>
              <Text style={styles.listSubtitle}>Conheça os sinais</Text>
            </View>
          </View>
          <MaterialCommunityIcons name="chevron-right" size={24} color="#999" />
        </TouchableOpacity>

        {/* Item Prevenção */}
        <TouchableOpacity 
          style={styles.listItem} 
          onPress={() => console.log("Navegar para Prevenção")}
        >
          <View style={styles.listLeft}>
            <MaterialCommunityIcons name="shield-check-outline" size={24} color="#333" style={styles.listIcon} />
            <View>
              <Text style={styles.listTitle}>Prevenção</Text>
              <Text style={styles.listSubtitle}>Conheça as formas de evitar</Text>
            </View>
          </View>
          <MaterialCommunityIcons name="chevron-right" size={24} color="#999" />
        </TouchableOpacity>

        {/* Item Campanhas */}
        <TouchableOpacity 
          style={styles.listItem} 
          onPress={() => console.log("Navegar para Campanhas")}
        >
          <View style={styles.listLeft}>
            <MaterialCommunityIcons name="bullhorn-outline" size={24} color="#333" style={styles.listIcon} />
            <View>
              <Text style={styles.listTitle}>Campanhas</Text>
              <Text style={styles.listSubtitle}>Fique por dentro das ações</Text>
            </View>
          </View>
          <MaterialCommunityIcons name="chevron-right" size={24} color="#999" />
        </TouchableOpacity>

      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  contentContainer: { padding: 15, paddingBottom: 100 },
  swiperContainer: {
    height: 180,
    borderRadius: 20,
    overflow: 'hidden',
    marginBottom: 20,
    backgroundColor: '#E0E0E0',
  },
  bannerImage: { width: '100%', height: '100%' },
  bannerOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 50,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  bannerText: { color: '#FFF', fontWeight: 'bold', fontSize: 16 },
  infoBox: {
    backgroundColor: '#E2F7F9',
    padding: 15,
    borderRadius: 15,
    marginBottom: 20,
  },
  infoText: { fontSize: 14, color: '#333', lineHeight: 20 },
  listContainer: { gap: 10 },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  listLeft: { flexDirection: 'row', alignItems: 'center' },
  listIcon: { marginRight: 15 },
  listTitle: { fontSize: 16, fontWeight: 'bold', color: '#000' },
  listSubtitle: { fontSize: 13, color: '#666' },
});