import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system/legacy';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { useState } from 'react';
import { Alert, Image, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function FocusFormScreen({ navigation }) {
  const [cep, setCep] = useState('');
  const [municipio, setMunicipio] = useState('');
  const [bairro, setBairro] = useState('');
  const [rua, setRua] = useState('');
  const [numero, setNumero] = useState('');
  const [descricao, setDescricao] = useState('');
  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  
  // Agora é um ARRAY para guardar até 5 imagens
  const [images, setImages] = useState([]); 
  const [loading, setLoading] = useState(false);

  // === LÓGICA DE IMAGENS ===
  const pickImageGaleria = async () => {
    if (images.length >= 5) {
      Alert.alert('Limite atingido', 'Você pode anexar no máximo 5 imagens.');
      return;
    }
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Aviso', 'Permissão negada para acessar a galeria.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.7,
      allowsMultipleSelection: true, // Permite selecionar várias de uma vez (no Android 11+)
      selectionLimit: 5 - images.length,
    });

    if (!result.canceled && result.assets) {
      const novasImagens = result.assets.map(asset => asset.uri);
      setImages(prev => [...prev, ...novasImagens].slice(0, 5));
    }
  };

  const pickImageCamera = async () => {
    if (images.length >= 5) {
      Alert.alert('Limite atingido', 'Você pode anexar no máximo 5 imagens.');
      return;
    }
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return;

    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 });
    
    if (!result.canceled && result.assets) {
      setImages(prev => [...prev, result.assets[0].uri]);
    }
  };

  const removerImagem = (indexParaRemover) => {
    setImages(prev => prev.filter((_, index) => index !== indexParaRemover));
  };

  // === LÓGICA DE GPS ===
  const handleGPS = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert("Aviso", "Permissão de localização negada.");
        return;
      }

      Alert.alert("GPS", "Buscando localização, aguarde...");
      const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
      const { latitude: lat, longitude: lon } = location.coords;

      setLatitude(String(lat));
      setLongitude(String(lon));

      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`,
        { headers: { 'User-Agent': 'VigiAA_Mobile_App' } }
      );
      
      const data = await response.json();
      if (data && data.address) {
        setCep(data.address.postcode || '');
        setMunicipio(data.address.city || data.address.town || data.address.village || '');
        setBairro(data.address.suburb || data.address.neighbourhood || '');
        setRua(data.address.road || '');
      }
    } catch (error) {
      Alert.alert("Erro", "Falha ao buscar o GPS.");
    }
  };

  // === LÓGICA DE ENVIO ===
  const handleSubmit = async () => {
    if (!municipio || !bairro || !rua || !numero) {
      Alert.alert("Aviso", "Preencha todos os campos obrigatórios (*).");
      return;
    }

    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('session_token');
      
      // 1. Envia os dados de texto para a nova rota do Django
      const responseText = await fetch(`${API_URL}/api/app-focos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          cep: cep,
          city: municipio,
          neighborhood: bairro,
          street: rua,
          number: numero,
          description: descricao,
          latitude: latitude,
          longitude: longitude
        })
      });

      if (responseText.ok) {
        const responseData = await responseText.json();
        const focusId = responseData.id; // Pegamos o ID que o Django acabou de criar!

        // 2. Faz o loop para enviar as imagens (se houver alguma)
        if (images.length > 0) {
          for (let uri of images) {
            await FileSystem.uploadAsync(
              `${API_URL}/api/app-focos/${focusId}/images/`,
              uri,
              {
                httpMethod: 'POST', 
                uploadType: 1, // Código nativo para MULTIPART
                fieldName: 'photo',
                mimeType: 'image/jpeg',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'ngrok-skip-browser-warning': 'true'
                },
              }
            );
          }
        }

        Alert.alert("Sucesso", "Foco e imagens cadastrados com sucesso!");
        navigation.goBack();
      } else {
        Alert.alert("Erro", "Falha ao salvar os dados do foco no banco.");
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <MaterialCommunityIcons name="chevron-left" size={32} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Focos de mosquitos</Text>
        <View style={{ width: 32 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        
        <TouchableOpacity style={styles.gpsButton} onPress={handleGPS}>
          <MaterialCommunityIcons name="map-marker" size={18} color="#FFF" style={{ marginRight: 8 }} />
          <Text style={styles.gpsButtonText}>Capturar localização pelo GPS</Text>
        </TouchableOpacity>

        <Text style={styles.mandatoryText}>
          Campos marcados com <Text style={{ color: 'red' }}>*</Text> são obrigatórios
        </Text>

        <View style={styles.formContainer}>
          <View style={styles.formRow}>
            <Text style={styles.label}>CEP</Text>
            <TextInput style={styles.input} placeholder="Digite o CEP" placeholderTextColor="#999" value={cep} onChangeText={setCep} keyboardType="numeric" />
          </View>
          <View style={styles.formRow}>
            <Text style={styles.label}>MUNICÍPIO<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Selecione a cidade" placeholderTextColor="#999" value={municipio} onChangeText={setMunicipio} />
            <MaterialCommunityIcons name="chevron-down" size={24} color="#666" />
          </View>
          <View style={styles.formRow}>
            <Text style={styles.label}>BAIRRO<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Selecione o bairro" placeholderTextColor="#999" value={bairro} onChangeText={setBairro} />
            <MaterialCommunityIcons name="chevron-down" size={24} color="#666" />
          </View>
          <View style={styles.formRow}>
            <Text style={styles.label}>RUA<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Digite o nome da rua" placeholderTextColor="#999" value={rua} onChangeText={setRua} />
            <MaterialCommunityIcons name="magnify" size={24} color="#000" />
          </View>
          <View style={styles.formRow}>
            <Text style={styles.label}>NÚMERO<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Digite o número" placeholderTextColor="#999" value={numero} onChangeText={setNumero} keyboardType="numeric" />
          </View>
          <View style={[styles.formRow, { alignItems: 'flex-start', borderBottomWidth: 0 }]}>
            <Text style={[styles.label, { marginTop: 15 }]}>DESCRIÇÃO</Text>
            <TextInput 
              style={[styles.input, styles.textArea]} 
              placeholder="Descreva a situação do local." 
              placeholderTextColor="#999"
              value={descricao} 
              onChangeText={setDescricao} 
              multiline 
            />
          </View>
        </View>

        {/* SEÇÃO DE IMAGENS COM MINIATURAS */}
        <View style={styles.imageSection}>
          <Text style={styles.imageLabel}>IMAGENS ({images.length}/5)</Text>
          
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.imageScrollContainer}>
            {/* Botões fixos de adicionar */}
            {images.length < 5 && (
              <>
                <TouchableOpacity style={styles.imageBtn} onPress={pickImageGaleria}>
                  <MaterialCommunityIcons name="image-multiple-outline" size={28} color="#555" />
                  <Text style={styles.imageBtnText}>Galeria</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.imageBtn} onPress={pickImageCamera}>
                  <MaterialCommunityIcons name="camera-outline" size={28} color="#555" />
                  <Text style={styles.imageBtnText}>Câmera</Text>
                </TouchableOpacity>
              </>
            )}

            {/* Renderização das Miniaturas */}
            {images.map((uri, index) => (
              <View key={index} style={styles.previewContainer}>
                <Image source={{ uri }} style={styles.previewImage} />
                <TouchableOpacity style={styles.removeImageBtn} onPress={() => removerImagem(index)}>
                  <MaterialCommunityIcons name="close" size={16} color="#FFF" />
                </TouchableOpacity>
              </View>
            ))}
          </ScrollView>
        </View>

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
          <Text style={styles.submitButtonText}>{loading ? "CADASTRANDO..." : "CADASTRAR"}</Text>
        </TouchableOpacity>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  header: { height: 100, paddingTop: 45, paddingHorizontal: 15, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#FFF', borderBottomWidth: 1, borderBottomColor: '#F0F0F0' },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#000' },
  backButton: { padding: 5 },
  scrollContent: { paddingHorizontal: 20, paddingBottom: 40, paddingTop: 20 },
  gpsButton: { backgroundColor: '#3AC0ED', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, borderRadius: 8, marginBottom: 15, marginHorizontal: 30 },
  gpsButtonText: { color: '#FFF', fontWeight: 'bold', fontSize: 14 },
  mandatoryText: { fontSize: 11, color: '#333', marginBottom: 15 },
  formContainer: { borderTopWidth: 1, borderTopColor: '#F0F0F0' },
  formRow: { flexDirection: 'row', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#F0F0F0', minHeight: 60 },
  label: { width: 100, fontSize: 12, fontWeight: 'bold', color: '#000' },
  input: { flex: 1, fontSize: 14, color: '#333', paddingVertical: 10 },
  textArea: { height: 80, textAlignVertical: 'top', marginTop: 5 },
  
  // Estilos da Galeria Nova
  imageSection: { marginTop: 10, borderTopWidth: 1, borderTopColor: '#F0F0F0', paddingTop: 15 },
  imageLabel: { fontSize: 12, fontWeight: 'bold', color: '#000', marginBottom: 10 },
  imageScrollContainer: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  imageBtn: { width: 80, height: 80, backgroundColor: '#F0F0F0', borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  imageBtnText: { fontSize: 11, color: '#555', marginTop: 5, fontWeight: '500' },
  
  // Estilo da Miniatura (Thumbnail)
  previewContainer: { width: 80, height: 80, borderRadius: 12, overflow: 'hidden', position: 'relative' },
  previewImage: { width: '100%', height: '100%', resizeMode: 'cover' },
  removeImageBtn: { position: 'absolute', top: 4, right: 4, backgroundColor: 'rgba(255,0,0,0.8)', width: 24, height: 24, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  
  submitButton: { backgroundColor: '#3AC0ED', height: 55, borderRadius: 8, alignItems: 'center', justifyContent: 'center', marginTop: 35 },
  submitButtonText: { color: '#000', fontWeight: 'bold', fontSize: 16 },
});