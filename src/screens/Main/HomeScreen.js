import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Image, StyleSheet, Text, View } from 'react-native';
import TabNavigator from '../../navigation/TabNavigator';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      {/* Cabeçalho Superior Fixo (Igual ao seu projeto em Kivy) */}
      <LinearGradient colors={['#3AC0ED', '#72FC90']} style={styles.header}>
        <View style={styles.headerLeft}>
          <Image source={require('../../../assets/images/react-logo.png')} style={styles.logo} />
          <Text style={styles.headerTitle}>VigiAA</Text>
        </View>
        <MaterialCommunityIcons name="bell-outline" size={24} color="#000" />
      </LinearGradient>

      {/* Container das Abas Inferiores */}
      <View style={styles.tabContainer}>
        <TabNavigator />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  header: {
    height: 80,
    paddingTop: 30,
    paddingHorizontal: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerLeft: { flexDirection: 'row', alignItems: 'center' },
  logo: { width: 30, height: 30, resizeMode: 'contain', marginRight: 10 },
  headerTitle: { fontSize: 22, fontWeight: 'bold', color: '#000' },
  tabContainer: { flex: 1 },
});