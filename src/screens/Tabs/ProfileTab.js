import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system/legacy';
import { Image } from 'expo-image';
import * as ImagePicker from 'expo-image-picker';
import { useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

// Componente reutilizável para cada linha de formulário (Edição Inline)
const ProfileField = ({ label, fieldKey, value, isReadOnly, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tempValue, setTempValue] = useState(value || '');

  // Sincroniza o valor temporário quando os dados da API chegam
  useEffect(() => {
    setTempValue(value || '');
  }, [value]);

  const handleSave = () => {
    onSave(fieldKey, tempValue);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setTempValue(value || '');
    setIsEditing(false);
  };

  return (
    <View style={styles.fieldContainer}>
      <Text style={styles.fieldLabel}>{label}</Text>
      
      <TextInput
        style={[styles.fieldInput, isEditing && styles.fieldInputEditing]}
        value={tempValue}
        onChangeText={setTempValue}
        editable={isEditing}
        selectTextOnFocus={isEditing}
        autoCapitalize="none"
      />

      <View style={styles.actionIcons}>
        {!isEditing ? (
          <TouchableOpacity 
            onPress={() => setIsEditing(true)} 
            disabled={isReadOnly}
            style={{ opacity: isReadOnly ? 0.3 : 1 }}
          >
            <MaterialCommunityIcons name="pencil-outline" size={22} color="#777" />
          </TouchableOpacity>
        ) : (
          <View style={styles.editingIcons}>
            <TouchableOpacity onPress={handleSave} style={styles.iconBtn}>
              <MaterialCommunityIcons name="check" size={24} color="#28A745" />
            </TouchableOpacity>
            <TouchableOpacity onPress={handleCancel} style={styles.iconBtn}>
              <MaterialCommunityIcons name="close" size={24} color="#DC3545" />
            </TouchableOpacity>
          </View>
        )}
      </View>
    </View>
  );
};

export default function ProfileTab({ navigation }) {
  const [userData, setUserData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarPerfilAPI();
  }, []);

  const carregarPerfilAPI = async () => {
    try {
      const token = await AsyncStorage.getItem('session_token');
      const response = await fetch(`${API_URL}/api/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(data);
      }
    } catch (error) {
      Alert.alert("Erro", "Falha ao carregar perfil.");
    } finally {
      setLoading(false);
    }
  };

  const atualizarCampoAPI = async (key, newValue) => {
    try {
      const token = await AsyncStorage.getItem('session_token');
      const response = await fetch(`${API_URL}/api/profile/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ [key]: newValue })
      });

      if (response.ok) {
        setUserData(prev => ({ ...prev, [key]: newValue }));
      } else {
        Alert.alert("Erro", "Não foi possível atualizar o dado.");
        carregarPerfilAPI(); // Reverte caso a API recuse
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão.");
    }
  };

  const alterarFoto = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Aviso', 'Precisamos de permissão para acessar suas fotos.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'], // Elimina o aviso de depreciação
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.7,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      uploadFotoAPI(result.assets[0]);
    }
  };

  const uploadFotoAPI = async (asset) => {
    try {
      const token = await AsyncStorage.getItem('session_token');
      
      const response = await FileSystem.uploadAsync(
        `${API_URL}/api/profile/`,
        asset.uri,
        {
          httpMethod: 'PATCH',
          uploadType: 1, // 1 é o código interno definitivo do Expo para MULTIPART
          fieldName: 'photo',
          mimeType: 'image/jpeg',
          headers: {
            'Authorization': `Bearer ${token}`,
            'ngrok-skip-browser-warning': 'true'
          },
        }
      );

      if (response.status === 200 || response.status === 201) {
        Alert.alert("Sucesso", "Foto atualizada!");
        carregarPerfilAPI();
      } else {
        console.log("Erro Django:", response.status, response.body);
        Alert.alert("Erro", "O servidor recusou a imagem.");
      }
    } catch (error) {
      console.log("Exceção upload (FileSystem):", error);
      Alert.alert("Erro", "Erro de conexão ao enviar imagem.");
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      "Excluir Conta",
      "Deseja desativar sua conta permanentemente?",
      [
        { text: "Cancelar", style: "cancel" },
        { 
          text: "Confirmar", 
          style: "destructive",
          onPress: async () => {
            const token = await AsyncStorage.getItem('session_token');
            await fetch(`${API_URL}/api/delete-account/`, {
              method: 'DELETE',
              headers: { 'Authorization': `Bearer ${token}`, 'ngrok-skip-browser-warning': 'true' }
            });
            handleLogout();
          }
        }
      ]
    );
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('session_token');
    await AsyncStorage.removeItem('user_email');
    navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
  };

  // Prepara a URL da foto com cache-buster (igual você fazia no Python)
  const getAvatarSource = () => {
    if (userData.photo) {
      const url = userData.photo.startsWith('http') ? userData.photo : `${API_URL}${userData.photo}`;
      return { uri: `${url}?t=${new Date().getTime()}` };
    }
    return require('../../../assets/images/react-logo.png'); // Foto padrão
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      
      {/* Área do Avatar com Câmera */}
      <View style={styles.headerProfile}>
        <View style={styles.avatarContainer}>
          <Image source={getAvatarSource()} style={styles.avatar} contentFit="cover" />
          <TouchableOpacity style={styles.cameraBadge} onPress={alterarFoto}>
            <MaterialCommunityIcons name="camera" size={20} color="#FFF" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Campos de Dados Pessoais (Edição Inline) */}
      <View style={styles.fieldsSection}>
        <ProfileField label="Nome" fieldKey="first_name" value={userData.first_name} onSave={atualizarCampoAPI} />
        <ProfileField label="Sobrenome" fieldKey="last_name" value={userData.last_name} onSave={atualizarCampoAPI} />
        <ProfileField label="Usuário" fieldKey="username" value={userData.username} onSave={atualizarCampoAPI} />
        <ProfileField label="Email" fieldKey="email" value={userData.email} isReadOnly={true} onSave={atualizarCampoAPI} />
      </View>

      {/* Botões de Ação */}
      <View style={styles.menuContainer}>
        {userData.tem_senha !== false && (
          <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('ChangePassword')}>
            <MaterialCommunityIcons name="key-outline" size={22} color="#333" style={styles.menuIcon} />
            <Text style={styles.menuText}>Redefinir senha</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={styles.menuItem} onPress={handleLogout}>
          <MaterialCommunityIcons name="logout" size={22} color="#333" style={styles.menuIcon} />
          <Text style={styles.menuText}>Sair da conta</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.menuItem, { borderBottomWidth: 0 }]} onPress={handleDeleteAccount}>
          <MaterialCommunityIcons name="delete-forever-outline" size={24} color="#D9534F" style={styles.menuIcon} />
          <Text style={[styles.menuText, { color: '#D9534F', fontWeight: 'bold' }]}>Excluir conta</Text>
        </TouchableOpacity>
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  headerProfile: { alignItems: 'center', paddingTop: 30, paddingBottom: 20 },
  avatarContainer: { width: 110, height: 110, borderRadius: 55, backgroundColor: '#E0E0E0', justifyContent: 'center', alignItems: 'center' },
  avatar: { width: 110, height: 110, borderRadius: 55 },
  cameraBadge: { position: 'absolute', bottom: 0, right: 0, backgroundColor: '#3AC0ED', width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', borderWidth: 3, borderColor: '#FFF' },
  
  fieldsSection: { paddingHorizontal: 15, marginBottom: 20 },
  fieldContainer: { flexDirection: 'row', alignItems: 'center', height: 55, borderBottomWidth: 1, borderBottomColor: '#EEE' },
  fieldLabel: { width: 90, fontSize: 14, fontWeight: 'bold', color: '#333' },
  fieldInput: { flex: 1, fontSize: 15, color: '#000', paddingVertical: 5 },
  fieldInputEditing: { borderBottomWidth: 1, borderBottomColor: '#3AC0ED' },
  actionIcons: { width: 60, alignItems: 'flex-end', justifyContent: 'center' },
  editingIcons: { flexDirection: 'row', gap: 10 },
  iconBtn: { padding: 5 },
  
  menuContainer: { borderTopWidth: 1, borderTopColor: '#EEE', marginTop: 10 },
  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 18, paddingHorizontal: 20, borderBottomWidth: 1, borderBottomColor: '#EEE' },
  menuIcon: { marginRight: 15 },
  menuText: { flex: 1, fontSize: 16, fontWeight: '600', color: '#000' },
});