import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';
import { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function CaseFormScreen({ navigation }) {
  const [dataNotificacao, setDataNotificacao] = useState('');
  const [cep, setCep] = useState('');
  const [municipio, setMunicipio] = useState('');
  const [bairro, setBairro] = useState('');
  const [rua, setRua] = useState('');
  const [numero, setNumero] = useState('');
  const [dataNascimento, setDataNascimento] = useState('');
  const [testePositivo, setTestePositivo] = useState(null); // null, true ou false

  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  const [loading, setLoading] = useState(false);

  // Função para aplicar máscara de data (DD/MM/AAAA)
  const formatData = (text) => {
    let limpo = text.replace(/\D/g, '').slice(0, 8);
    if (limpo.length >= 5) {
      return `${limpo.slice(0, 2)}/${limpo.slice(2, 4)}/${limpo.slice(4)}`;
    } else if (limpo.length >= 3) {
      return `${limpo.slice(0, 2)}/${limpo.slice(2)}`;
    }
    return limpo;
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
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`,
        { headers: { 'User-Agent': 'VigiAA_Mobile_App' } }
      );
      
      const data = await response.json();
      if (data && data.address) {
        setCep(data.address.postcode || '');
        setMunicipio(data.address.city || data.address.town || data.address.village || '');
        setBairro(data.address.suburb || data.address.neighbourhood || '');
        setRua(data.address.road || '');
        Alert.alert("Sucesso", "Endereço preenchido com base na sua localização!");
      }
    } catch (error) {
      Alert.alert("Erro", "Falha ao buscar o GPS.");
    }
  };

  // === LÓGICA DE ENVIO ===
  const handleSubmit = async () => {
    if (!dataNotificacao || !municipio || !bairro || !rua || !numero || !dataNascimento || testePositivo === null) {
      Alert.alert("Aviso", "Preencha todos os campos obrigatórios (*).");
      return;
    }

    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('session_token');
      
      // O payload deve bater exatamente com o DengueCaseSerializer do seu views.py
      const payload = {
        notification_date: dataNotificacao,
        cep: cep,
        city: municipio,
        neighborhood: bairro,
        street: rua,
        number: numero,
        birth_date: dataNascimento,
        positive_test: testePositivo,
        latitude: latitude,
        longitude: longitude
      };

      const response = await fetch(`${API_URL}/api/report-case/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        if (testePositivo) {
          Alert.alert(
            "Aviso de Teste Positivo", 
            "O paciente deve ser identificado. A Secretaria de Saúde entrará em contato.",
            [{ text: "OK", onPress: () => navigation.goBack() }] // Aqui no futuro chamaremos a tela PositiveCase
          );
        } else {
          Alert.alert("Sucesso", "Caso suspeito registrado com sucesso!");
          navigation.goBack();
        }
      } else {
        Alert.alert("Erro", "Falha ao salvar os dados no banco.");
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
        <Text style={styles.headerTitle}>Casos de dengue</Text>
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
            <Text style={styles.label}>Data da notificação<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput 
              style={styles.input} 
              placeholder="DD/MM/AAAA" 
              placeholderTextColor="#999" 
              value={dataNotificacao} 
              onChangeText={(text) => setDataNotificacao(formatData(text))} 
              keyboardType="numeric" 
            />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>CEP</Text>
            <TextInput style={styles.input} placeholder="Digite o CEP" placeholderTextColor="#999" value={cep} onChangeText={setCep} keyboardType="numeric" />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>MUNICÍPIO<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Selecione o nome da cidade" placeholderTextColor="#999" value={municipio} onChangeText={setMunicipio} />
            <MaterialCommunityIcons name="chevron-down" size={24} color="#666" />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>BAIRRO<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Selecione o nome do bairro" placeholderTextColor="#999" value={bairro} onChangeText={setBairro} />
            <MaterialCommunityIcons name="chevron-down" size={24} color="#666" />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>RUA<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Selecione o nome da rua" placeholderTextColor="#999" value={rua} onChangeText={setRua} />
            <MaterialCommunityIcons name="chevron-down" size={24} color="#666" />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>NÚMERO<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput style={styles.input} placeholder="Digite o número" placeholderTextColor="#999" value={numero} onChangeText={setNumero} keyboardType="numeric" />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>Data de nascimento<Text style={{ color: 'red' }}>*</Text></Text>
            <TextInput 
              style={styles.input} 
              placeholder="DD/MM/AAAA" 
              placeholderTextColor="#999" 
              value={dataNascimento} 
              onChangeText={(text) => setDataNascimento(formatData(text))} 
              keyboardType="numeric" 
            />
          </View>

          <View style={styles.formRow}>
            <Text style={styles.label}>Teste positivo<Text style={{ color: 'red' }}>*</Text></Text>
            
            <View style={styles.radioGroup}>
              <TouchableOpacity style={styles.radioOption} onPress={() => setTestePositivo(true)}>
                <MaterialCommunityIcons name={testePositivo === true ? "radiobox-marked" : "radiobox-blank"} size={22} color="#000" />
                <Text style={styles.radioText}>Sim</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.radioOption} onPress={() => setTestePositivo(false)}>
                <MaterialCommunityIcons name={testePositivo === false ? "radiobox-marked" : "radiobox-blank"} size={22} color="#000" />
                <Text style={styles.radioText}>Não</Text>
              </TouchableOpacity>
            </View>
          </View>

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
  
  label: { width: 110, fontSize: 12, fontWeight: 'bold', color: '#000' },
  input: { flex: 1, fontSize: 14, color: '#333', paddingVertical: 10 },
  
  radioGroup: { flex: 1, flexDirection: 'row', alignItems: 'center', paddingVertical: 10 },
  radioOption: { flexDirection: 'row', alignItems: 'center', marginRight: 25 },
  radioText: { fontSize: 14, color: '#000', marginLeft: 8 },
  
  submitButton: { backgroundColor: '#3AC0ED', height: 55, borderRadius: 8, alignItems: 'center', justifyContent: 'center', marginTop: 35 },
  submitButtonText: { color: '#000', fontWeight: 'bold', fontSize: 16 },
});