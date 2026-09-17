import { MaterialCommunityIcons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { LinearGradient } from 'expo-linear-gradient';
import { Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import ExploreTab from '../screens/Tabs/ExploreTab';
import HomeTab from '../screens/Tabs/HomeTab';
import NewTab from '../screens/Tabs/NewTab';
import ProfileTab from '../screens/Tabs/ProfileTab';

const Tab = createBottomTabNavigator();

// Cabeçalho Global (mantido intacto)
const CustomHeader = () => (
  <LinearGradient 
    colors={['#3AC0ED', '#72FC90']} 
    start={{ x: 0, y: 0 }} 
    end={{ x: 1, y: 0 }} 
    style={styles.header}
  >
    <View style={styles.headerLeft}>
      <Image source={require('../../assets/images/logo-sem-fundo.png')} style={styles.logo} />
      <Text style={styles.headerTitle}>VigiAA</Text>
    </View>
    <TouchableOpacity onPress={() => console.log('Abrir notificações')}>
      <MaterialCommunityIcons name="bell-outline" size={26} color="#000" />
    </TouchableOpacity>
  </LinearGradient>
);

export default function TabNavigator() {
  // 1. Pegamos a medida exata da barra de navegação do celular
  const insets = useSafeAreaInsets();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
        header: () => <CustomHeader />,
        tabBarStyle: { 
          backgroundColor: '#3AC0ED', 
          // 2. Altura base (60) + o tamanho da barra do sistema
          height: 60 + insets.bottom, 
          // 3. Empurra os ícones para cima exatamente o tamanho da barra
          paddingBottom: insets.bottom > 0 ? insets.bottom : 10, 
          paddingTop: 10,
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
    paddingTop: 45, 
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