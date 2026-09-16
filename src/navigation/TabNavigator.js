import { MaterialCommunityIcons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import ExploreTab from '../screens/Tabs/ExploreTab';
import HomeTab from '../screens/Tabs/HomeTab';
import NewTab from '../screens/Tabs/NewTab';
import ProfileTab from '../screens/Tabs/ProfileTab';

// Telas temporárias para as outras abas (depois substituiremos pelos seus arquivos de abas)
function DummyScreen() { return <View />; }

const Tab = createBottomTabNavigator();

export default function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { backgroundColor: '#3AC0ED', height: 60, paddingBottom: 8 },
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