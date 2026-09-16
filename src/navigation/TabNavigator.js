import { MaterialCommunityIcons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { LinearGradient } from 'expo-linear-gradient';
import { Image, Platform, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

import ExploreTab from '../screens/Tabs/ExploreTab';
import HomeTab from '../screens/Tabs/HomeTab';
import NewTab from '../screens/Tabs/NewTab';
import ProfileTab from '../screens/Tabs/ProfileTab';

const Tab = createBottomTabNavigator();

// Componente do Cabeçalho Global (igual à sua imagem de referência)
const CustomHeader = () => (
  <LinearGradient 
    colors={['#3AC0ED', '#72FC90']} 
    start={{ x: 0, y: 0 }} 
    end={{ x: 1, y: 0 }} 
    style={styles.header}
  >
    <View style={styles.headerLeft}>
      {/* Ajuste o nome do arquivo da logo se necessário */}
      <Image source={require('../../assets/images/logo-sem-fundo.png')} style={styles.logo} />
      <Text style={styles.headerTitle}>VigiAA</Text>
    </View>
    <TouchableOpacity onPress={() => console.log('Abrir notificações')}>
      <MaterialCommunityIcons name="bell-outline" size={26} color="#000" />
    </TouchableOpacity>
  </LinearGradient>
);

export default function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,             // 1. Habilita o cabeçalho superior
        header: () => <CustomHeader />, // 2. Injeta o nosso cabeçalho customizado
        tabBarStyle: { 
          backgroundColor: '#3AC0ED', 
          height: Platform.OS === 'ios' ? 85 : 70,       // Mais alto para evitar a barra do sistema
          paddingBottom: Platform.OS === 'ios' ? 25 : 15, // Empurra os ícones para cima
          paddingTop: 5,
        },
        tabBarActiveTintColor: '#000',
        tabBarInactiveTintColor: 'rgba(0,0,0,0.5)',
      }}
    >
      <Tab.Screen 
        name="TabHome" 
        component={HomeTab} 
        options={{
          title: 'Início',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="home" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="TabNew" 
        component={NewTab} 
        options={{
          title: 'Novo',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="plus-circle-outline" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="TabExplore" 
        component={ExploreTab} 
        options={{
          title: 'Explorar',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="compass" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="TabProfile" 
        component={ProfileTab} 
        options={{
          title: 'Perfil',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="account" size={size} color={color} />
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  header: {
    height: 100,
    paddingTop: 45, // Espaço para a barra de status (bateria/relógio) do celular
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logo: {
    width: 35,
    height: 35,
    resizeMode: 'contain',
    marginRight: 10,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#000',
  },
});
