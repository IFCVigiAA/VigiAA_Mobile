import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Image } from 'expo-image';
import { useEffect, useState } from 'react';
import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function ProfileTab({ navigation }) {
  const [userName, setUserName] = useState('Usuário VigiAA');
  const [userEmail, setUserEmail] = useState('carregando...');

  useEffect(() => {
    carregarDadosUsuario();
  }, []);

  const carregarDadosUsuario = async () => {
    try {
      // Se você salvou dados do usuário no AsyncStorage durante o login, pode recuperá-los aqui
      const emailSalvo = await AsyncStorage.getItem('user_email');
      if (emailSalvo) {
        setUserEmail(emailSalvo);
      } else {
        setUserEmail('vigiaa@ifc.edu.br');
      }
    } catch (error) {
      setUserEmail('Erro ao carregar dados');
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      "Sair",
      "Deseja realmente sair da sua conta?",
      [
        { text: "Cancelar", style: "cancel" },
        { 
          text: "Sair", 
          style: "destructive",
          onPress: async () => {
            await AsyncStorage.removeItem('session_token');
            await AsyncStorage.removeItem('user_email');
            // Reseta a navegação voltando direto para a tela de Login
            navigation.reset({
              index: 0,
              routes: [{ name: 'Login' }],
            });
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Cabeçalho do Perfil */}
      <View style={styles.headerProfile}>
        <View style={styles.avatarContainer}>
          <Image 
            source={require('../../../assets/images/react-logo.png')} 
            style={styles.avatar} 
          />
        </View>
        <Text style={styles.nameText}>{userName}</Text>
        <Text style={styles.emailText}>{userEmail}</Text>
      </View>

      {/* Lista de Ações do Perfil */}
      <View style={styles.menuContainer}>
        
        <TouchableOpacity style={styles.menuItem} onPress={() => Alert.alert("Em desenvolvimento", "Função de editar perfil.")}>
          <MaterialCommunityIcons name="account-edit-outline" size={22} color="#333" style={styles.menuIcon} />
          <Text style={styles.menuText}>Editar Perfil</Text>
          <MaterialCommunityIcons name="chevron-right" size={20} color="#999" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => Alert.alert("VigiAA Mobile", "Versão 1.0.0 - Instituto Federal Catarinense")}>
          <MaterialCommunityIcons name="information-outline" size={22} color="#333" style={styles.menuIcon} />
          <Text style={styles.menuText}>Sobre o Aplicativo</Text>
          <MaterialCommunityIcons name="chevron-right" size={20} color="#999" />
        </TouchableOpacity>

        {/* Botão de Sair */}
        <TouchableOpacity style={[styles.menuItem, styles.logoutItem]} onPress={handleLogout}>
          <MaterialCommunityIcons name="logout" size={22} color="#D9534F" style={styles.menuIcon} />
          <Text style={[styles.menuText, { color: '#D9534F', fontWeight: 'bold' }]}>Encerrar Sessão</Text>
        </TouchableOpacity>

      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  headerProfile: {
    backgroundColor: '#FFF',
    padding: 30,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  avatarContainer: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: '#E2F7F9',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
    elevation: 2,
  },
  avatar: { width: 50, height: 50, resizeMode: 'contain' },
  nameText: { fontSize: 20, fontWeight: 'bold', color: '#000', marginBottom: 5 },
  emailText: { fontSize: 14, color: '#666' },
  menuContainer: {
    marginTop: 20,
    backgroundColor: '#FFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E0E0E0',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  menuIcon: { marginRight: 15 },
  menuText: { flex: 1, fontSize: 16, color: '#333' },
  logoutItem: {
    borderBottomWidth: 0,
    marginTop: 5,
  },
});